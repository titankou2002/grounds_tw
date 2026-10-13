/* 藍圖頁面所見即所得編輯（登入的編輯者）：
   - 點頁面上的文字直接改，離開欄位自動儲存
   - 條列項目可新增、刪除；段落／表格列可刪除
   - 左邊目錄可拖曳換順序、可刪除章節（右邊內容跟著動）
   - 每章標題旁有狀態標籤
   所有人（含日本同事、未登入）看到同一份最新內容。
   資料存在 Supabase bp_content（key='edits'），與原始頁面分開，原文不會被破壞。 */
(function () {
  'use strict';
  var SUPABASE_URL = 'https://wvslwxbdfcqbsnihvwnb.supabase.co';
  var SUPABASE_KEY = 'sb_publishable_dnpBAxgX5cNpiVsRGncILg_8zXEL7gD';
  var STATUS = { todo: '未開始', doing: '進行中', waiting_japan: '等日本', done: '完成' };
  var EDITABLE = '.chapter-title, .bullet-grid li, .callout p, .matrix-desc, .matrix-table td, .two-col li, .col-title, .intent p, .intent li';
  var LANG = document.documentElement.lang || 'ja';

  var main = document.querySelector('.blueprint-content');
  var toc = document.querySelector('aside.toc');
  var sections = document.querySelectorAll('section.chapter');
  if (!main || !toc || !sections.length) return;

  var sb, tenantId = null, isMember = false, isAdminUser = false, canEdit = false, userName = '', user = null;
  var edits = {};
  var targets = [];
  var saveTimer = null;

  function h(tag, attrs) {
    var el = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === 'class') el.className = attrs[k];
      else if (k.slice(0, 2) === 'on') el.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] !== false && attrs[k] != null) el.setAttribute(k, attrs[k] === true ? '' : attrs[k]);
    }
    for (var i = 2; i < arguments.length; i++) {
      var c = arguments[i];
      if (c == null || c === false) continue;
      el.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    }
    return el;
  }

  var css = document.createElement('style');
  css.textContent =
    '.lp-edit [data-lpk]{outline:1px dashed transparent;outline-offset:3px;border-radius:3px;cursor:text;transition:outline-color .15s}' +
    '.lp-edit [data-lpk]:hover{outline-color:rgba(120,120,110,.55)}' +
    '.lp-edit [data-lpk]:focus{outline:2px solid #b7791f;background:rgba(183,121,31,.07)}' +
    '.lp-chip{font:inherit;font-size:12px;border:1px solid currentColor;border-radius:99px;padding:1px 10px;margin-left:10px;background:transparent;vertical-align:middle}' +
    '.lp-chip.doing{color:#b7791f}.lp-chip.waiting_japan{color:#b4452f}.lp-chip.done{color:#2f7d4f}.lp-chip.todo{color:#9a978f}' +
    'select.lp-chip{cursor:pointer;color:inherit;background:var(--bg)}' +
    '.lp-x{font:inherit;font-size:15px;line-height:1;border:0;background:transparent;color:var(--muted);cursor:pointer;padding:0 6px;opacity:0;transition:opacity .15s}' +
    '.lp-edit :hover>.lp-x,.lp-edit .lp-x:focus{opacity:1}.lp-x:hover{color:#b4452f}' +
    '.lp-edit .lp-unit{position:relative}' +
    '.lp-add{font:inherit;font-size:13px;border:1px dashed var(--line);background:transparent;color:var(--muted);border-radius:99px;padding:3px 14px;margin-top:10px;cursor:pointer}' +
    '.lp-add:hover{color:var(--fg);border-color:var(--fg)}' +
    '.lp-drag{cursor:grab}.lp-over{box-shadow:0 -2px 0 #b7791f}' +
    '.lp-bar{position:fixed;right:16px;bottom:16px;z-index:99;display:flex;gap:10px;align-items:center;background:var(--fg);color:var(--bg);padding:8px 14px;border-radius:99px;font-size:13px;box-shadow:0 2px 10px rgba(0,0,0,.25);max-width:92vw;flex-wrap:wrap}' +
    '.lp-bar button{font:inherit;font-size:12.5px;border:1px solid currentColor;background:transparent;color:inherit;padding:2px 10px;border-radius:99px;cursor:pointer}';
  document.head.appendChild(css);

  var bar = h('div', { class: 'lp-bar' });
  function setBar(msg) {
    bar.textContent = '';
    bar.appendChild(h('span', null, msg));
    for (var i = 1; i < arguments.length; i++) if (arguments[i]) bar.appendChild(arguments[i]);
    if (!bar.parentNode) document.body.appendChild(bar);
  }
  function btn(label, fn) { return h('button', { onclick: fn }, label); }
  var loginBtn = function () {
    return btn('登入編輯', function () {
      sb.auth.signInWithOAuth({ provider: 'google', options: { redirectTo: location.href.split('#')[0] } });
    });
  };
  var logoutBtn = function () { return btn('登出', function () { sb.auth.signOut().then(function () { location.reload(); }); }); };
  var restoreBtn = function () {
    return btn('復原刪除', function () {
      if (!confirm('把已刪除的章節和內容全部復原？')) return;
      Object.keys(edits).forEach(function (k) { if (k.indexOf('d|') === 0) delete edits[k]; });
      delete edits.hidden;
      saveNow(true);
    });
  };

  // ───── 收集：依「章 id + 序號」給穩定 key（必須在改動 DOM 之前） ─────
  function collect() {
    Array.prototype.forEach.call(sections, function (sec) {
      var id = sec.id || 'sec';
      Array.prototype.forEach.call(sec.querySelectorAll(EDITABLE), function (el, i) {
        targets.push({ el: el, key: LANG + '|' + id + '|' + i, orig: el.textContent, sec: sec });
      });
      Array.prototype.forEach.call(sec.querySelectorAll('.bullet-grid'), function (g, gi) {
        g.setAttribute('data-lpg', LANG + '|' + id + '|' + gi);
      });
    });
  }

  function unitOf(el) { return el.matches('td') ? el.closest('tr') : el; }

  function applyContent() {
    targets.forEach(function (t) {
      var e = edits[t.key];
      if (e && e.orig === t.orig && typeof e.text === 'string') t.el.textContent = e.text;
      var d = edits['d|' + t.key];
      var u = unitOf(t.el);
      if (d === t.orig && !t.el.matches('.chapter-title')) u.style.display = 'none';
    });
    // 新增的條列項目
    document.querySelectorAll('.bullet-grid').forEach(function (g) {
      g.querySelectorAll('li.lp-new').forEach(function (x) { x.remove(); });
      var arr = edits['add|' + g.getAttribute('data-lpg')] || [];
      arr.forEach(function (txt, i) { g.appendChild(makeNew(g, arr, i)); });
    });
    applyOrder();
  }

  function makeNew(g, arr, i) {
    var key = 'add|' + g.getAttribute('data-lpg');
    var li = h('li', { class: 'lp-new lp-unit' }, arr[i]);
    if (canEdit) {
      li.setAttribute('data-lpk', key + '|' + i);
      li.setAttribute('contenteditable', 'plaintext-only');
      if (li.contentEditable !== 'plaintext-only') li.setAttribute('contenteditable', 'true');
      li.addEventListener('keydown', function (ev) { if (ev.key === 'Enter') { ev.preventDefault(); li.blur(); } });
      li.addEventListener('blur', function () {
        var now = li.textContent.replace('×', '').trim();
        var cur = edits[key] || [];
        if (!now) { cur.splice(i, 1); } else if (cur[i] === now) return; else cur[i] = now;
        edits[key] = cur; queueSave(); applyContent(); decorate();
      });
    }
    return li;
  }

  function renderChip(sec) {
    var old = sec.querySelector('.lp-chip');
    if (old) old.remove();
    var title = sec.querySelector('.chapter-title');
    if (!title) return;
    var st = edits['status|' + sec.id] || 'todo';
    var chip;
    if (canEdit) {
      chip = h('select', { class: 'lp-chip ' + st, onchange: function () {
        edits['status|' + sec.id] = this.value; this.className = 'lp-chip ' + this.value; queueSave();
      } });
      Object.keys(STATUS).forEach(function (k) {
        chip.appendChild(h('option', { value: k, selected: k === st ? true : false }, STATUS[k]));
      });
    } else {
      if (!edits['status|' + sec.id]) return;
      chip = h('span', { class: 'lp-chip ' + st }, STATUS[st]);
    }
    title.insertAdjacentElement('afterend', chip);
  }

  // ───── 章節順序／隱藏（左邊目錄與右邊內容同步） ─────
  function tocLinks() { return Array.prototype.slice.call(toc.querySelectorAll('a[href*="#"]')); }
  function idOf(a) { return a.getAttribute('href').split('#')[1]; }
  var baseOrder = tocLinks().map(idOf);

  function applyOrder() {
    var order = (edits.order || []).filter(function (id) { return baseOrder.indexOf(id) >= 0; });
    baseOrder.forEach(function (id) { if (order.indexOf(id) < 0) order.push(id); });
    var links = {}; tocLinks().forEach(function (a) { links[idOf(a)] = a; });
    var secs = {}; Array.prototype.forEach.call(sections, function (s) { secs[s.id] = s; });
    // 目錄：依新順序重新排進原位
    var firstLink = links[baseOrder[0]], anchorParent = firstLink && firstLink.parentNode;
    if (anchorParent) {
      var marker = h('span'); firstLink.parentNode.insertBefore(marker, firstLink);
      order.forEach(function (id) { if (links[id]) anchorParent.insertBefore(links[id], marker); });
      marker.remove();
    }
    // 內容：把章節放回原本佔的位置（保留結尾等未列入目錄的區塊位置）
    var slots = baseOrder.map(function (id) { return secs[id]; }).filter(Boolean);
    var holders = slots.map(function (s) { var m = h('span'); s.parentNode.insertBefore(m, s); return m; });
    slots.forEach(function (s) { s.remove(); });
    order.forEach(function (id, i) { if (secs[id] && holders[i]) holders[i].parentNode.insertBefore(secs[id], holders[i]); });
    holders.forEach(function (m) { m.remove(); });
    // 隱藏與重新編號
    var hidden = edits.hidden || [], n = 0;
    order.forEach(function (id) {
      var gone = hidden.indexOf(id) >= 0;
      if (links[id]) links[id].style.display = gone ? 'none' : '';
      if (secs[id]) secs[id].style.display = gone ? 'none' : '';
      if (gone) return;
      n++;
      var num = ('0' + n).slice(-2);
      var np = secs[id] && secs[id].querySelector('.chapter-num');
      if (np && /^\d+$/.test(np.textContent.trim())) np.textContent = num;
      if (links[id]) {
        var m = links[id].getAttribute('data-lpt');
        if (m === null) { m = links[id].textContent.replace(/^\d+\s—\s/, ''); links[id].setAttribute('data-lpt', m); }
        if (/^\d+\s—\s/.test(links[id].textContent) || links[id].hasAttribute('data-lpnum')) {
          links[id].setAttribute('data-lpnum', '1');
          setLinkText(links[id], num + ' — ' + m);
        }
      }
    });
  }
  function setLinkText(a, txt) {
    var x = a.querySelector('.lp-x');
    a.textContent = txt;
    if (x) a.appendChild(x);
  }

  // ───── 儲存 ─────
  function queueSave() { setBar('儲存中…'); clearTimeout(saveTimer); saveTimer = setTimeout(function () { saveNow(false); }, 600); }
  function saveNow(reload) {
    sb.from('bp_content').upsert({ tenant_id: tenantId, key: 'edits', data: edits }, { onConflict: 'tenant_id,key' })
      .then(function (r) {
        if (r.error) setBar('存檔失敗：' + r.error.message, logoutBtn());
        else if (reload) location.reload();
        else setBar('已儲存・' + userName + ' 編輯中', restoreBtn(), logoutBtn());
      });
  }

  // ───── 編輯功能 ─────
  function xBtn(label, fn) {
    return h('button', { class: 'lp-x', title: label, onclick: function (ev) { ev.preventDefault(); ev.stopPropagation(); fn(); } }, '×');
  }

  function decorate() {
    document.querySelectorAll('.lp-x, .lp-add').forEach(function (e) { e.remove(); });
    // 條列項目、段落、表格列：刪除鈕
    targets.forEach(function (t) {
      if (t.el.matches('.chapter-title, .col-title, .matrix-desc')) return;
      var u = unitOf(t.el);
      if (u.style.display === 'none') return;
      u.classList.add('lp-unit');
      var host = t.el.matches('td') ? t.el : u;
      if (t.el.matches('td') && t.el !== u.querySelector('td:last-child')) return;
      host.appendChild(xBtn('刪除', function () {
        if (!confirm('刪除這一項？\n' + t.el.textContent.trim().slice(0, 60))) return;
        edits['d|' + t.key] = t.orig; queueSave(); applyContent(); decorate();
      }));
    });
    document.querySelectorAll('li.lp-new').forEach(function (li) {
      var g = li.parentNode, key = 'add|' + g.getAttribute('data-lpg');
      var i = Array.prototype.indexOf.call(g.querySelectorAll('li.lp-new'), li);
      li.appendChild(xBtn('刪除', function () {
        var cur = edits[key] || []; cur.splice(i, 1); edits[key] = cur; queueSave(); applyContent(); decorate();
      }));
    });
    // 新增條列
    document.querySelectorAll('.bullet-grid').forEach(function (g) {
      var key = 'add|' + g.getAttribute('data-lpg');
      g.insertAdjacentElement('afterend', h('button', { class: 'lp-add', onclick: function () {
        var txt = prompt('新增項目：');
        if (!txt || !txt.trim()) return;
        var cur = edits[key] || []; cur.push(txt.trim()); edits[key] = cur; queueSave(); applyContent(); decorate();
      } }, '＋ 新增項目'));
    });
    // 章節：右邊「刪除此章」＋左邊目錄 ×
    Array.prototype.forEach.call(sections, function (sec) {
      var link = toc.querySelector('a[href$="#' + sec.id + '"]');
      if (!link) return;
      var del = function () {
        var name = (sec.querySelector('.chapter-title') || {}).textContent || sec.id;
        if (!confirm('刪除整章「' + name + '」？\n（可用右下角「復原刪除」找回）')) return;
        edits.hidden = (edits.hidden || []).concat([sec.id]); queueSave(); applyContent();
      };
      link.appendChild(xBtn('刪除此章', del));
      var t = sec.querySelector('.chapter-title');
      if (t) t.insertAdjacentElement('afterend', h('button', { class: 'lp-add lp-x', style: 'opacity:1;margin-left:10px', onclick: del }, '刪除此章'));
    });
  }

  function enableDrag() {
    var dragId = null;
    tocLinks().forEach(function (a) {
      a.setAttribute('draggable', 'true'); a.classList.add('lp-drag');
      a.addEventListener('dragstart', function (e) { dragId = idOf(a); e.dataTransfer.effectAllowed = 'move'; try { e.dataTransfer.setData('text/plain', dragId); } catch (_) {} });
      a.addEventListener('dragover', function (e) { if (dragId) { e.preventDefault(); a.classList.add('lp-over'); } });
      a.addEventListener('dragleave', function () { a.classList.remove('lp-over'); });
      a.addEventListener('drop', function (e) {
        e.preventDefault(); a.classList.remove('lp-over');
        var to = idOf(a);
        if (!dragId || dragId === to) return;
        var order = tocLinks().map(idOf);
        order.splice(order.indexOf(dragId), 1);
        order.splice(order.indexOf(to), 0, dragId);
        edits.order = order; dragId = null; queueSave(); applyOrder();
      });
      a.addEventListener('dragend', function () { dragId = null; });
    });
  }

  function enableEditing() {
    document.body.classList.add('lp-edit');
    targets.forEach(function (t) {
      t.el.setAttribute('data-lpk', t.key);
      t.el.setAttribute('contenteditable', 'plaintext-only');
      if (t.el.contentEditable !== 'plaintext-only') t.el.setAttribute('contenteditable', 'true');
      t.el.addEventListener('keydown', function (ev) { if (ev.key === 'Enter') { ev.preventDefault(); t.el.blur(); } });
      t.el.addEventListener('blur', function () {
        var now = t.el.textContent.replace(/×$/, '').trim();
        var cur = edits[t.key] ? edits[t.key].text : t.orig;
        if (now === cur.trim()) return;
        if (now === t.orig.trim()) delete edits[t.key];
        else edits[t.key] = { orig: t.orig, text: now };
        queueSave();
      });
    });
    enableDrag();
    applyContent();
    decorate();
    setBar('編輯模式：點文字直接改・目錄可拖曳、可刪除・' + userName, restoreBtn(), logoutBtn());
  }


  // ───── AI 聊天框（登入的成員才有） ─────
  var CHAT_URL = 'https://script.google.com/macros/s/AKfycbyZog9Sw2JpEX0EsEyyunM3oTbvVQBoKiwQnj3B8SNLHRtrjpmFadoli9ioohLIH_a_1A/exec';
  var CHAT_RULES =
    '你是 grounds Taiwan（日本品牌 grounds 在台灣開店）專案的助理，用繁體中文，簡短直接，不要客套廢話。' +
    '先參考下面的藍圖頁面內容；頁面沒寫的，就用你的一般知識（台灣開店、公司設立、法規、進口、行銷等）直接回答，' +
    '並標明「（一般說法，請向會計師／專業人士確認）」。不確定的數字或法規要說不確定，不要編造。輸出純文字，不要使用 ** 或 # 等 Markdown 符號。';
  function initChat() {
    var hist = [];
    var cs = document.createElement('style');
    cs.textContent =
      '.lp-chatbtn{position:fixed;left:16px;bottom:16px;z-index:99;font:inherit;font-size:13px;background:var(--fg);color:var(--bg);border:0;border-radius:99px;padding:9px 16px;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.25)}' +
      '.lp-chat{position:fixed;left:16px;bottom:64px;z-index:99;width:min(380px,calc(100vw - 32px));height:min(520px,70vh);background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.3);display:none;flex-direction:column;overflow:hidden}' +
      '.lp-chat.open{display:flex}.lp-msgs{flex:1;overflow:auto;padding:12px;font-size:14px;line-height:1.6}' +
      '.lp-m{margin:0 0 10px;white-space:pre-wrap}.lp-m.me{text-align:right;color:var(--muted)}' +
      '.lp-m.ai{background:var(--callout-bg,#f4f3ee);padding:8px 10px;border-radius:8px}' +
      '.lp-in{display:flex;gap:6px;padding:8px;border-top:1px solid var(--line)}' +
      '.lp-in input{flex:1;font:inherit;font-size:14px;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:7px 10px}' +
      '.lp-in button{font:inherit;font-size:13px;border:0;background:var(--fg);color:var(--bg);border-radius:8px;padding:0 14px;cursor:pointer}';
    document.head.appendChild(cs);
    var msgs = h('div', { class: 'lp-msgs' }, h('p', { class: 'lp-m ai' }, '問我關於這份藍圖的任何事，例如：「現在卡在哪？」「週五要請日本決定什麼？」'));
    var input = h('input', { placeholder: '輸入問題，按 Enter', autocomplete: 'off' });
    var panel = h('div', { class: 'lp-chat' }, msgs,
      h('form', { class: 'lp-in', onsubmit: function (e) { e.preventDefault(); ask(); } }, input, h('button', { type: 'submit' }, '送出')));
    var toggle = h('button', { class: 'lp-chatbtn', onclick: function () { panel.classList.toggle('open'); if (panel.classList.contains('open')) input.focus(); } }, '問 AI');
    document.body.appendChild(panel); document.body.appendChild(toggle);
    function add(cls, text) { var p = h('p', { class: 'lp-m ' + cls }, text); msgs.appendChild(p); msgs.scrollTop = msgs.scrollHeight; return p; }
    function ask() {
      var q = input.value.trim(); if (!q) return; input.value = '';
      add('me', q);
      var wait = add('ai', '思考中…');
      var ctx = Array.prototype.filter.call(sections, function (s) { return s.style.display !== 'none'; })
        .map(function (s) { return s.innerText.replace(/×/g, ''); }).join('\n\n');
      sb.auth.getSession().then(function (r) {
        var tok = r.data.session ? r.data.session.access_token : '';
        return fetch(CHAT_URL, { method: 'POST', headers: { 'Content-Type': 'text/plain' },
          body: JSON.stringify({ action: 'bpchat', token: tok, question: q, context: ctx, history: hist, system: CHAT_RULES }) })
          .then(function (res) { return res.json(); });
      }).then(function (d) {
        if (d && d.answer) { hist.push({ role: 'user', text: q }, { role: 'ai', text: d.answer }); wait.textContent = d.answer.replace(/\*\*/g, '').replace(/^\s*[*-]\s+/gm, '・').replace(/^#+\s*/gm, ''); }
        else wait.textContent = '（出錯：' + ((d && d.error) || '失敗了') + '）';
        msgs.scrollTop = msgs.scrollHeight;
      }).catch(function (e) { wait.textContent = '（出錯：' + e.message + '）'; });
    }
  }

  function load() {
    return sb.from('bp_content').select('data').eq('tenant_id', tenantId).eq('key', 'edits').maybeSingle().then(function (r) {
      if (!r.error && r.data) edits = r.data.data || {};
    });
  }

  function start() {
    sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true } });
    collect();
    sb.auth.getSession().then(function (r) {
      user = r.data.session ? r.data.session.user : null;
      return user ? sb.rpc('accept_invites') : null;
    }).then(function () {
      return sb.rpc('bp_tenant_id', { p_slug: 'grounds' });
    }).then(function (t) {
      tenantId = t.data;
      if (!tenantId || !user) return;
      return sb.from('members').select('user_id,display_name,role,active').eq('tenant_id', tenantId).then(function (m) {
        var me = (m.data || []).filter(function (x) { return x.user_id === user.id && x.active; })[0];
        if (me) { isMember = true; isAdminUser = me.role === 'admin'; userName = me.display_name; canEdit = me.role === 'admin' || me.role === 'manager'; }
      });
    }).then(function () {
      if (!tenantId) return;
      return load();
    }).then(function () {
      if (canEdit) enableEditing();
      else {
        applyContent();
        if (user) setBar(user.email + '（無編輯權限）', logoutBtn());
        else setBar('唯讀', loginBtn());
      }
      if (isAdminUser) initChat();
      if (location.hash) { var el = document.getElementById(location.hash.slice(1)); if (el) el.scrollIntoView(); }
    }).catch(function () { /* 載入失敗不影響閱讀 */ });
    document.addEventListener('visibilitychange', function () {
      if (!document.hidden && tenantId && !canEdit) load().then(applyContent);
    });
  }

  var s = document.createElement('script');
  s.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/dist/umd/supabase.min.js';
  s.onload = start;
  document.head.appendChild(s);
})();
