# -*- coding: utf-8 -*-
"""부록 「일본어 한자」 페이지 생성 — 교재(Session_*.html)에 실제로 나온 ruby 한자만 모은다.

저장소 루트에서:  python tools/build_kanji.py
- 세션의 <ruby>漢字<rt>かな</rt></ruby> 를 전부 훑어 (한자, 독음) 쌍을 모은다.
- 뜻 · 사전형은 tools/kanji_dict.json (키 "한자|독음") 에서 가져온다.
- 사전에 없는 새 쌍이 있으면 목록을 찍고 멈춘다(종료 코드 1) → 사전에 추가한 뒤 다시 실행.
- 가격(390円 등) 은 단어가 아니라서 뺀다.
"""
import collections
import datetime
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT = os.path.join(ROOT, 'tools', 'kanji_dict.json')
W = '월화수목금토일'
FW = str.maketrans('０１２３４５６７８９', '0123456789')


def collect():
    pairs = collections.OrderedDict()
    for f in sorted(glob.glob(os.path.join(ROOT, 'Session_*.html'))):
        d = os.path.basename(f)[8:16]
        s = re.sub(r'data:[^"]*', '', open(f, encoding='utf-8').read()).split('<body>', 1)[1]
        for m in re.finditer(r'<ruby>([^<]+)<rp>（</rp><rt>([^<]+)</rt><rp>）</rp></ruby>', s):
            if re.fullmatch(r'[\d,０-９]+円', m[1]):
                continue
            k = m[1] + '|' + m[2]
            p = pairs.setdefault(k, {'sessions': set()})
            p['sessions'].add(d)
    return pairs


# ── romaji (헵번 · 장음 마크론, 사이트 규칙) ──
DIG = {'きゃ': 'kya', 'きゅ': 'kyu', 'きょ': 'kyo', 'しゃ': 'sha', 'しゅ': 'shu', 'しょ': 'sho', 'ちゃ': 'cha',
       'ちゅ': 'chu', 'ちょ': 'cho', 'にゃ': 'nya', 'にゅ': 'nyu', 'にょ': 'nyo', 'ひゃ': 'hya', 'ひゅ': 'hyu',
       'ひょ': 'hyo', 'みゃ': 'mya', 'みゅ': 'myu', 'みょ': 'myo', 'りゃ': 'rya', 'りゅ': 'ryu', 'りょ': 'ryo',
       'ぎゃ': 'gya', 'ぎゅ': 'gyu', 'ぎょ': 'gyo', 'じゃ': 'ja', 'じゅ': 'ju', 'じょ': 'jo', 'びゃ': 'bya',
       'びゅ': 'byu', 'びょ': 'byo', 'ぴゃ': 'pya', 'ぴゅ': 'pyu', 'ぴょ': 'pyo', 'ちぇ': 'che', 'しぇ': 'she', 'じぇ': 'je'}
MONO = dict(zip('あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん'
                'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽぁぃぅぇぉ',
                'a i u e o ka ki ku ke ko sa shi su se so ta chi tsu te to na ni nu ne no ha hi fu he ho '
                'ma mi mu me mo ya yu yo ra ri ru re ro wa o n ga gi gu ge go za ji zu ze zo da ji zu de do '
                'ba bi bu be bo pa pi pu pe po a i u e o'.split()))
MAC = {'a': 'ā', 'i': 'ī', 'u': 'ū', 'e': 'ē', 'o': 'ō'}


def hira(s):
    return ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s)


def romaji(kana, pos=''):
    k = hira(kana)
    syl = []
    i = 0
    while i < len(k):
        if k[i:i + 2] in DIG:
            syl.append(DIG[k[i:i + 2]]); i += 2
        elif k[i] in MONO:
            syl.append(MONO[k[i]]); i += 1
        else:
            syl.append(k[i]); i += 1
    out = []
    gem = False
    for j, s in enumerate(syl):
        if s == 'っ':
            gem = True; continue
        if s == 'ー' and out:
            out[-1] = out[-1][:-1] + MAC.get(out[-1][-1], out[-1][-1]); continue
        if gem:
            s = ('t' + s) if s.startswith('ch') else (s[0] + s); gem = False
        if out and s in ('u', 'o') and out[-1][-1:] == 'o' and not (s == 'u' and pos == '동사' and j == len(syl) - 1):
            out[-1] = out[-1][:-1] + 'ō'; continue
        if out and s == 'u' and out[-1][-1:] == 'u':
            out[-1] = out[-1][:-1] + 'ū'; continue
        if out and s == 'a' and out[-1][-1:] == 'a':
            out[-1] = out[-1][:-1] + 'ā'; continue
        if out and s == 'e' and out[-1][-1:] == 'e':
            out[-1] = out[-1][:-1] + 'ē'; continue
        if out and out[-1] == 'n' and s[0] in 'aiueoy':
            out[-1] = "n'"
        out.append(s)
    r = ''.join(out)
    return r


# ── 단어에 ruby 붙이기 (한자 · 숫자 덩어리에만 독음) ──
BASE = r'[0-9一-鿿々〇ヵヶ、]'


def ruby(word, reading):
    parts = re.findall(BASE + '+|[^0-9一-鿿々〇ヵヶ、]+', word)
    pat = ''
    for p in parts:
        pat += '(.+?)' if re.match(BASE, p) else '(' + re.escape(hira(p)) + ')'
    m = re.fullmatch(pat, reading)
    if not m:
        return f'<ruby>{word}<rp>（</rp><rt>{reading}</rt><rp>）</rp></ruby>'
    out = ''
    for p, g in zip(parts, m.groups()):
        out += f'<ruby>{p}<rp>（</rp><rt>{g}</rt><rp>）</rp></ruby>' if re.match(BASE, p) else p
    return out


def mmdd(d):
    w = W[datetime.date(int(d[:4]), int(d[4:6]), int(d[6:])).weekday()]
    return f'{d[4:6]}/{d[6:]}({w})'


def main():
    pairs = collect()
    dic = json.load(open(DICT, encoding='utf-8'))
    missing = [k for k in pairs if k not in dic]
    if missing:
        print('사전에 없는 (한자|독음) — tools/kanji_dict.json 에 추가 필요:')
        for k in missing:
            print('  ', k, sorted(pairs[k]['sessions']))
        sys.exit(1)
    words = collections.OrderedDict()
    for k, p in pairs.items():
        e = dic[k]
        w = e['word'].translate(FW)
        key = (w, e['word_reading'])
        x = words.setdefault(key, {'word': w, 'reading': e['word_reading'], 'pos': e['pos'], 'ko': e['ko'],
                                   'sessions': set()})
        x['sessions'] |= p['sessions']
    items = sorted(words.values(), key=lambda x: (min(x['sessions']), x['reading']))
    kanji = {c for x in items for c in x['word'] if '一' <= c <= '鿿' or c == '々'}
    by_month = collections.OrderedDict()
    for x in items:
        by_month.setdefault(min(x['sessions'])[4:6], []).append(x)
    today = datetime.date.today()
    upd = f'{today:%Y.%m.%d}({W[today.weekday()]})'
    secs = []
    for mm, xs in by_month.items():
        cards = []
        for x in xs:
            first = min(x['sessions'])
            proper = x['pos'] == '기타'
            ro = romaji(x['reading'], x['pos'])
            if proper:
                ro = ro[:1].upper() + ro[1:]
            search = ' '.join([x['word'], x['reading'], ro, x['ko']])
            cards.append(
                f'<div class="kj-card" data-q="{html.escape(search)}">'
                f'<div class="kj-word" lang="ja">{ruby(x["word"], x["reading"])}</div>'
                f'<div class="kj-ro">{ro}</div><div class="kj-ko">{html.escape(x["ko"])}</div>'
                f'<div class="kj-meta"><span class="kj-pos">{x["pos"]}</span>'
                f'<button class="kj-src" data-file="Session_{first}.html" title="처음 나온 수업 열기">{mmdd(first)}</button></div></div>')
        secs.append(f'<section class="kj-sec" data-m="{mm}"><div class="kj-sec-head">{int(mm)}월 교재'
                    f'<span class="kj-sec-cnt">{len(xs)}단어</span></div><div class="kj-grid">{"".join(cards)}</div></section>')
    chips = ''.join(f'<button class="kj-chip" data-m="{mm}">{int(mm)}월</button>' for mm in by_month)
    js = r'''<script>
(function(){
var q=document.getElementById('kj-q'),cur='all';
function apply(){var t=q.value.trim().toLowerCase(),n=0;
 document.querySelectorAll('.kj-sec').forEach(function(s){var vis=0;
  var mOk=(cur==='all'||s.dataset.m===cur);
  s.querySelectorAll('.kj-card').forEach(function(c){var ok=mOk&&(!t||c.dataset.q.toLowerCase().indexOf(t)>=0);c.style.display=ok?'':'none';if(ok)vis++;});
  s.style.display=vis?'':'none';n+=vis;});
 document.getElementById('kj-count').textContent=n+'단어';
 document.getElementById('kj-empty').hidden=n>0;}
q.addEventListener('input',apply);
document.querySelectorAll('.kj-chip').forEach(function(b){b.onclick=function(){cur=b.dataset.m;
 document.querySelectorAll('.kj-chip').forEach(function(x){x.classList.toggle('active',x===b);});apply();};});
document.querySelectorAll('.kj-hide').forEach(function(b){b.onclick=function(){var c='hide-'+b.dataset.h,on=document.body.classList.toggle(c);
 b.classList.toggle('primary',on);document.querySelectorAll('.kj-card.show').forEach(function(x){x.classList.remove('show');});};});
document.querySelectorAll('.kj-card').forEach(function(c){c.addEventListener('click',function(e){if(e.target.closest('.kj-src'))return;
 if(/hide-/.test(document.body.className))c.classList.toggle('show');});});
document.querySelectorAll('.kj-src').forEach(function(b){b.onclick=function(){var f=b.dataset.file;
 if(window.parent!==window)window.parent.postMessage({openSession:f},'*');else location.href=f;};});
apply();
})();
</script>'''
    page = ('<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">'
            '<link rel="stylesheet" href="assets/fonts.css" />\n<link rel="stylesheet" href="assets/session.css" />\n'
            '<link rel="stylesheet" href="assets/appendix.css" />\n'
            '<title>부록 · 일본어 한자 · 넥슨게임즈</title></head><body>\n'
            '<div class="topbar"><a href="index.html" onclick="if(window.parent!==window){window.parent.postMessage(\'showHome\',\'*\');return false;}">← 홈</a>'
            f'<span class="topbar-sep">|</span><span class="topbar-title">부록 · 일본어 한자</span><span class="topbar-date">{upd} 갱신</span></div>\n'
            '<div class="page">\n'
            '<div class="page-header"><div class="date-badge">부록</div><h1>일본어 한자 (<span lang="ja">漢字</span>)</h1>'
            f'<div class="subtitle">교재에 나온 한자 단어 {len(items)}개 · 한자 {len(kanji)}자 · 새 교재가 추가되면 함께 갱신된다</div></div>\n'
            '<div class="appx-tools sticky kj-tools">'
            '<input id="kj-q" class="kj-search" type="search" placeholder="한자 · 독음 · 로마자 · 뜻으로 찾기" aria-label="단어 찾기">'
            '<button class="appx-btn kj-hide" data-h="rt">독음 가리기</button>'
            '<button class="appx-btn kj-hide" data-h="ro">로마자 가리기</button>'
            '<button class="appx-btn kj-hide" data-h="ko">뜻 가리기</button>'
            '<span class="kj-count" id="kj-count"></span></div>\n'
            f'<div class="kj-chips"><button class="kj-chip active" data-m="all">전체</button>{chips}</div>\n'
            '<div class="appx-note">가리기를 켠 뒤 카드를 누르면 그 카드만 보인다. 날짜를 누르면 그 단어가 처음 나온 수업이 열린다.</div>\n'
            + ''.join(secs) +
            '<div class="appx-note center" id="kj-empty" hidden>찾는 단어가 없다.</div>\n'
            f'</div>\n{js}\n</body></html>\n')
    open(os.path.join(ROOT, 'Appendix_Kanji.html'), 'w', encoding='utf-8', newline='\n').write(page)
    print('Appendix_Kanji.html', len(items), 'words', len(kanji), 'kanji', 'months', list(by_month))


if __name__ == '__main__':
    main()
