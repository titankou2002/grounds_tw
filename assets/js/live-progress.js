/* 藍圖頁面內嵌進度：每章底下直接顯示、直接修改該章任務（狀態／條件／備註）。
   資料在 Supabase（與 progress.html 共用）；未登入＝唯讀，登入的編輯者可直接改。 */
(function () {
  'use strict';
  var SUPABASE_URL = 'https://wvslwxbdfcqbsnihvwnb.supabase.co';
  var SUPABASE_KEY = 'sb_publishable_dnpBAxgX5cNpiVsRGncILg_8zXEL7gD';
  var TENANT_SLUG = 'grounds';
  var STATUS = { todo: '未開始', doing: '進行中', waiting_japan: '等日本', done: '完成' };

  var sections = document.querySelectorAll('section.chapter');
  if (!sections.length || !document.querySelector('.blueprint-layout')) return;

  var S = { tenantId: null, rows: {}, chapters: {}, canEdit: false, name: '', user: null };
  var sb;

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
  function rowOf(id) { return S.rows[id] || { status: 'todo', conditions_done: [], note: '' }; }

  var css = document.createElement('style');
  css.textContent =
    '.lp{margin-top:28px;padding:20px 24px;border:1px solid var(--line);border-radius:4px}' +
    '.lp-head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:6px}' +
    '.lp-title{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0}' +
    '.lp-who{font-size:12.5px;color:var(--muted);display:flex;gap:8px;align-items:center}' +
    '.lp-btn{font:inherit;font-size:12.5px;border:1px solid var(--line);background:transparent;color:var(--fg);padding:3px 10px;border-radius:99px;cursor:pointer}' +
    '.lp-task{border-top:1px dashed var(--line);padding:12px 0}' +
    '.lp-row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}' +
    '.lp-name{font-weight:500;flex:1;min-width:200px;font-size:14.5px}' +
    '.lp-name.done{text-decoration:line-through;color:var(--muted)}' +
    '.lp-dot{width:9px;height:9px;border-radius:50%;background:#9a978f;flex:none}' +
    '.lp-dot.doing{background:#b7791f}.lp-dot.waiting_japan{background:#b4452f}.lp-dot.done{background:#2f7d4f}' +
    '.lp select,.lp textarea{font:inherit;font-size:13.5px;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:4px 8px}' +
    '.lp textarea{width:100%;min-height:54px;margin-top:8px}' +
    '.lp-cond{display:flex;gap:8px;align-items:flex-start;font-size:13.5px;margin-top:6px}' +
    '.lp-cond input{margin-top:4px}' +
    '.lp-ro{font-size:13px;color:var(--muted);margin:6px 0 0;white-space:pre-wrap}' +
    '.lp-meta{font-size:12px;color:var(--muted);margin-top:4px}' +
    '.lp-toast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);background:var(--fg);color:var(--bg);padding:8px 16px;border-radius:99px;font-size:13.5px;z-index:99}';
  document.head.appendChild(css);

  var toastEl;
  function toast(msg) {
    if (toastEl) toastEl.remove();
    toastEl = h('div', { class: 'lp-toast' }, msg);
    document.body.appendChild(toastEl);
    setTimeout(function () { if (toastEl) toastEl.remove(); }, 2500);
  }

  function save(t, patch) {
    if (!S.canEdit) return;
    var cur = rowOf(t.id);
    var next = {
      status: patch.status != null ? patch.status : cur.status,
      conditions_done: patch.conditions_done != null ? patch.conditions_done : (cur.conditions_done || []),
      note: patch.note != null ? patch.note : (cur.note || '')
    };
    var before = S.rows[t.id];
    S.rows[t.id] = Object.assign({}, cur, next, { updated_by_name: S.name, updated_at: new Date().toISOString() });
    renderAll();
    sb.from('bp_task_state').upsert(
      { tenant_id: S.tenantId, task_id: t.id, status: next.status, conditions_done: next.conditions_done, note: next.note },
      { onConflict: 'tenant_id,task_id' }
    ).then(function (r) {
      if (r.error) {
        if (before) S.rows[t.id] = before; else delete S.rows[t.id];
        renderAll(); toast('存檔失敗：' + r.error.message);
      } else toast('已儲存');
    });
  }

  function taskView(t) {
    var row = rowOf(t.id), st = row.status, done = row.conditions_done || [];
    var box = h('div', { class: 'lp-task' });
    var head = h('div', { class: 'lp-row' }, h('span', { class: 'lp-dot ' + st }),
      h('span', { class: 'lp-name' + (st === 'done' ? ' done' : '') }, t.title));
    if (S.canEdit) {
      var sel = h('select', { onchange: function () { save(t, { status: this.value }); } });
      Object.keys(STATUS).forEach(function (k) {
        sel.appendChild(h('option', { value: k, selected: k === st ? true : false }, STATUS[k]));
      });
      head.appendChild(sel);
    } else head.appendChild(h('span', { class: 'lp-ro' }, STATUS[st]));
    box.appendChild(head);

    t.conditions.forEach(function (c, i) {
      var cb = h('input', { type: 'checkbox', checked: done.indexOf(i) >= 0, disabled: !S.canEdit, onchange: function () {
        var set = (rowOf(t.id).conditions_done || []).slice(), at = set.indexOf(i);
        if (this.checked && at < 0) set.push(i);
        if (!this.checked && at >= 0) set.splice(at, 1);
        set.sort(function (a, b) { return a - b; });
        var p = { conditions_done: set };
        if (this.checked && rowOf(t.id).status === 'todo') p.status = 'doing';
        save(t, p);
      } });
      box.appendChild(h('label', { class: 'lp-cond' }, cb, h('span', null, c.text)));
    });

    if (S.canEdit) {
      box.appendChild(h('textarea', { placeholder: '備註／留言（卡在哪、日本回覆了什麼…）', onblur: function () {
        if (this.value !== (rowOf(t.id).note || '')) save(t, { note: this.value });
      } }, row.note || ''));
    } else if (row.note) box.appendChild(h('p', { class: 'lp-ro' }, row.note));
    if (row.updated_at) {
      var d = new Date(row.updated_at);
      box.appendChild(h('div', { class: 'lp-meta' }, '最後更新：' + (row.updated_by_name || '') + ' ' + (d.getMonth() + 1) + '/' + d.getDate() + ' ' + ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2)));
    }
    return box;
  }

  function who() {
    var el = h('div', { class: 'lp-who' });
    if (S.canEdit) {
      el.appendChild(h('span', null, S.name));
      el.appendChild(h('button', { class: 'lp-btn', onclick: function () { sb.auth.signOut().then(function () { location.reload(); }); } }, '登出'));
    } else if (S.user) {
      el.appendChild(h('span', null, S.user.email + '（無編輯權限）'));
    } else {
      el.appendChild(h('span', null, '唯讀'));
      el.appendChild(h('button', { class: 'lp-btn', onclick: function () {
        sb.auth.signInWithOAuth({ provider: 'google', options: { redirectTo: location.href.split('#')[0] } });
      } }, '登入編輯'));
    }
    return el;
  }

  function renderAll() {
    document.querySelectorAll('.lp').forEach(function (e) { e.remove(); });
    Array.prototype.forEach.call(sections, function (sec) {
      var numEl = sec.querySelector('.chapter-num');
      if (!numEl) return;
      var ch = S.chapters[parseInt(numEl.textContent, 10)];
      if (!ch || !ch.tasks.length) return;
      var done = ch.tasks.filter(function (t) { return rowOf(t.id).status === 'done'; }).length;
      var panel = h('div', { class: 'lp' },
        h('div', { class: 'lp-head' }, h('p', { class: 'lp-title' }, '進度（' + done + '/' + ch.tasks.length + ' 完成）'), who()));
      ch.tasks.forEach(function (t) { panel.appendChild(taskView(t)); });
      sec.appendChild(panel);
    });
  }

  function load() {
    return sb.from('bp_content').select('data').eq('tenant_id', S.tenantId).eq('key', 'tasks').maybeSingle().then(function (r) {
      if (r.error || !r.data) return;
      r.data.data.chapters.forEach(function (c) { S.chapters[c.num] = c; });
      return sb.from('bp_task_state').select('*').eq('tenant_id', S.tenantId);
    }).then(function (r) {
      if (!r || r.error) return;
      S.rows = {}; r.data.forEach(function (x) { S.rows[x.task_id] = x; });
    });
  }

  function start() {
    sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true } });
    sb.auth.getSession().then(function (r) {
      S.user = r.data.session ? r.data.session.user : null;
      return S.user ? sb.rpc('accept_invites') : null;
    }).then(function () {
      return sb.rpc('bp_tenant_id', { p_slug: TENANT_SLUG });
    }).then(function (t) {
      S.tenantId = t.data;
      if (!S.tenantId) return;
      if (!S.user) return;
      return sb.from('members').select('user_id,display_name,role,active').eq('tenant_id', S.tenantId).then(function (m) {
        var me = (m.data || []).filter(function (x) { return x.user_id === S.user.id && x.active; })[0];
        if (me) { S.name = me.display_name; S.canEdit = me.role === 'admin' || me.role === 'manager'; }
      });
    }).then(function () {
      if (!S.tenantId) return;
      return load().then(renderAll);
    }).catch(function () { /* 進度載入失敗不影響藍圖閱讀 */ });
    document.addEventListener('visibilitychange', function () {
      if (!document.hidden && S.tenantId) load().then(renderAll);
    });
  }

  var s = document.createElement('script');
  s.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/dist/umd/supabase.min.js';
  s.onload = start;
  document.head.appendChild(s);
})();
