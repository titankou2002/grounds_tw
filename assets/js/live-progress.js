/* 藍圖頁面所見即所得編輯：登入的編輯者直接點頁面上的文字就能改，離開欄位自動儲存；
   每章有狀態標籤可直接點選。所有人（含日本同事、未登入）看到的是同一份最新內容。
   資料存在 Supabase bp_content（key = 'edits'），與原始頁面分開，原文不會被破壞。 */
(function () {
  'use strict';
  var SUPABASE_URL = 'https://wvslwxbdfcqbsnihvwnb.supabase.co';
  var SUPABASE_KEY = 'sb_publishable_dnpBAxgX5cNpiVsRGncILg_8zXEL7gD';
  var TENANT_SLUG = 'grounds';
  var STATUS = { todo: '未開始', doing: '進行中', waiting_japan: '等日本', done: '完成' };
  var EDITABLE = '.chapter-title, .bullet-grid li, .callout p, .matrix-desc, .matrix-table td, .two-col li, .col-title, .intent p, .intent li';
  var LANG = document.documentElement.lang || 'ja';

  var sections = document.querySelectorAll('section.chapter');
  if (!sections.length || !document.querySelector('.blueprint-layout')) return;

  var sb, tenantId = null, canEdit = false, userName = '', user = null;
  var edits = {};       // { 'zh|sec|i': {orig, text}, 'status|sec': 'doing' }
  var targets = [];     // [{el, key, orig}]
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
    '.lp-bar{position:fixed;right:16px;bottom:16px;z-index:99;display:flex;gap:10px;align-items:center;background:var(--fg);color:var(--bg);padding:8px 14px;border-radius:99px;font-size:13px;box-shadow:0 2px 10px rgba(0,0,0,.25)}' +
    '.lp-bar button{font:inherit;font-size:12.5px;border:1px solid currentColor;background:transparent;color:inherit;padding:2px 10px;border-radius:99px;cursor:pointer}';
  document.head.appendChild(css);

  var bar = h('div', { class: 'lp-bar' });
  function setBar(msg, btn) {
    bar.textContent = '';
    bar.appendChild(h('span', null, msg));
    if (btn) bar.appendChild(btn);
    if (!bar.parentNode) document.body.appendChild(bar);
  }
  var loginBtn = function () {
    return h('button', { onclick: function () {
      sb.auth.signInWithOAuth({ provider: 'google', options: { redirectTo: location.href.split('#')[0] } });
    } }, '登入編輯');
  };
  var logoutBtn = function () {
    return h('button', { onclick: function () { sb.auth.signOut().then(function () { location.reload(); }); } }, '登出');
  };

  // ───── 找出可編輯的元素，給穩定的 key ─────
  function collect() {
    Array.prototype.forEach.call(sections, function (sec) {
      var id = sec.id || 'sec';
      Array.prototype.forEach.call(sec.querySelectorAll(EDITABLE), function (el, i) {
        if (el.closest('.lp-bar')) return;
        var orig = el.textContent;
        targets.push({ el: el, key: LANG + '|' + id + '|' + i, orig: orig });
      });
    });
  }

  function applyEdits() {
    targets.forEach(function (t) {
      var e = edits[t.key];
      if (e && e.orig === t.orig && typeof e.text === 'string') t.el.textContent = e.text;
    });
    Array.prototype.forEach.call(sections, function (sec) { renderChip(sec); });
  }

  function renderChip(sec) {
    var old = sec.querySelector('.lp-chip');
    if (old) old.remove();
    var numEl = sec.querySelector('.chapter-title');
    if (!numEl) return;
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
      if (st === 'todo' && !edits['status|' + sec.id]) return;
      chip = h('span', { class: 'lp-chip ' + st }, STATUS[st]);
    }
    numEl.insertAdjacentElement('afterend', chip);
  }

  // ───── 儲存 ─────
  function queueSave() {
    setBar('儲存中…');
    clearTimeout(saveTimer);
    saveTimer = setTimeout(doSave, 600);
  }
  function doSave() {
    sb.from('bp_content').upsert({ tenant_id: tenantId, key: 'edits', data: edits }, { onConflict: 'tenant_id,key' })
      .then(function (r) {
        if (r.error) setBar('存檔失敗：' + r.error.message, logoutBtn());
        else setBar('已儲存・' + userName + ' 編輯中', logoutBtn());
      });
  }

  function enableEditing() {
    document.body.classList.add('lp-edit');
    targets.forEach(function (t) {
      t.el.setAttribute('data-lpk', t.key);
      t.el.setAttribute('contenteditable', 'plaintext-only');
      if (t.el.contentEditable !== 'plaintext-only') t.el.setAttribute('contenteditable', 'true');
      t.el.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter') { ev.preventDefault(); t.el.blur(); }
      });
      t.el.addEventListener('blur', function () {
        var now = t.el.textContent.trim();
        var cur = edits[t.key] ? edits[t.key].text : t.orig;
        if (now === cur) return;
        if (now === t.orig.trim()) delete edits[t.key];
        else edits[t.key] = { orig: t.orig, text: now };
        queueSave();
      });
    });
    setBar('編輯模式：直接點文字修改，離開欄位自動儲存・' + userName, logoutBtn());
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
      return sb.rpc('bp_tenant_id', { p_slug: TENANT_SLUG });
    }).then(function (t) {
      tenantId = t.data;
      if (!tenantId || !user) return;
      return sb.from('members').select('user_id,display_name,role,active').eq('tenant_id', tenantId).then(function (m) {
        var me = (m.data || []).filter(function (x) { return x.user_id === user.id && x.active; })[0];
        if (me) { userName = me.display_name; canEdit = me.role === 'admin' || me.role === 'manager'; }
      });
    }).then(function () {
      if (!tenantId) return;
      return load();
    }).then(function () {
      applyEdits();
      if (canEdit) enableEditing();
      else if (user) setBar(user.email + '（無編輯權限）', logoutBtn());
      else setBar('唯讀', loginBtn());
    }).catch(function () { /* 載入失敗不影響閱讀 */ });
    document.addEventListener('visibilitychange', function () {
      if (!document.hidden && tenantId && !canEdit) load().then(applyEdits);
    });
  }

  var s = document.createElement('script');
  s.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/dist/umd/supabase.min.js';
  s.onload = start;
  document.head.appendChild(s);
})();
