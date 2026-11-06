# -*- coding: utf-8 -*-
"""부록 「히라가나」 · 「카타가나」 페이지 생성. 저장소 루트에서: python tools/build_kana.py"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEION = [
    ('あ', ['あa', 'いi', 'うu', 'えe', 'おo']), ('か', ['かka', 'きki', 'くku', 'けke', 'こko']),
    ('さ', ['さsa', 'しshi', 'すsu', 'せse', 'そso']), ('た', ['たta', 'ちchi', 'つtsu', 'てte', 'とto']),
    ('な', ['なna', 'にni', 'ぬnu', 'ねne', 'のno']), ('は', ['はha', 'ひhi', 'ふfu', 'へhe', 'ほho']),
    ('ま', ['まma', 'みmi', 'むmu', 'めme', 'もmo']), ('や', ['やya', None, 'ゆyu', None, 'よyo']),
    ('ら', ['らra', 'りri', 'るru', 'れre', 'ろro']), ('わ', ['わwa', None, None, None, 'をo']),
    ('ん', ['んn', None, None, None, None])]
DAKU = [('が', ['がga', 'ぎgi', 'ぐgu', 'げge', 'ごgo']), ('ざ', ['ざza', 'じji', 'ずzu', 'ぜze', 'ぞzo']),
        ('だ', ['だda', 'ぢji', 'づzu', 'でde', 'どdo']), ('ば', ['ばba', 'びbi', 'ぶbu', 'べbe', 'ぼbo'])]
HANDAKU = [('ぱ', ['ぱpa', 'ぴpi', 'ぷpu', 'ぺpe', 'ぽpo'])]
YOON = [('き', ['きゃkya', 'きゅkyu', 'きょkyo']), ('し', ['しゃsha', 'しゅshu', 'しょsho']),
        ('ち', ['ちゃcha', 'ちゅchu', 'ちょcho']), ('に', ['にゃnya', 'にゅnyu', 'にょnyo']),
        ('ひ', ['ひゃhya', 'ひゅhyu', 'ひょhyo']), ('み', ['みゃmya', 'みゅmyu', 'みょmyo']),
        ('り', ['りゃrya', 'りゅryu', 'りょryo']), ('ぎ', ['ぎゃgya', 'ぎゅgyu', 'ぎょgyo']),
        ('じ', ['じゃja', 'じゅju', 'じょjo']), ('び', ['びゃbya', 'びゅbyu', 'びょbyo']),
        ('ぴ', ['ぴゃpya', 'ぴゅpyu', 'ぴょpyo'])]
GAIRAI = [('ファ', 'fa'), ('フィ', 'fi'), ('フェ', 'fe'), ('フォ', 'fo'), ('ティ', 'ti'), ('ディ', 'di'),
          ('デュ', 'dyu'), ('ウィ', 'wi'), ('ウェ', 'we'), ('ウォ', 'wo'), ('シェ', 'she'), ('ジェ', 'je'),
          ('チェ', 'che'), ('ヴァ', 'va')]
GAIRAI_EX = [('コーヒー', 'Kōhī', '커피'), ('パソコン', 'Pasokon', '컴퓨터'), ('カメラ', 'Kamera', '카메라'),
             ('スマホ', 'Sumaho', '스마트폰'), ('チケット', 'Chiketto', '티켓'), ('ケーキ', 'Kēki', '케이크'),
             ('パーティー', 'Pātī', '파티'), ('ファイル', 'Fairu', '파일')]


def kata(s):
    return ''.join(chr(ord(c) + 0x60) if 'ぁ' <= c <= 'ゖ' else c for c in s)


def split(cell):
    i = 0
    while i < len(cell) and not cell[i].isascii():
        i += 1
    return cell[:i], cell[i:]


def cell_html(k, r):
    return f'<td class="kc"><div class="kana-main" lang="ja">{k}</div><div class="kana-ro">{r}</div></td>'


def table(rows, cols, conv):
    head = ''.join(f'<th>{c}</th>' for c in cols)
    out = [f'<table class="kana-table appx-kana"><thead><tr><th></th>{head}</tr></thead><tbody>']
    for name, cells in rows:
        tds = []
        for c in cells:
            if c is None:
                tds.append('<td class="kc-empty"></td>')
                continue
            k, r = split(c)
            tds.append(cell_html(conv(k), r))
        label = conv(name) if name == 'ん' else conv(name) + '行'
        out.append(f'<tr><th lang="ja">{label}</th>{"".join(tds)}</tr>')
    out.append('</tbody></table>')
    return ''.join(out)


def page(kind):
    is_k = kind == 'kata'
    conv = kata if is_k else (lambda s: s)
    name = '카타가나' if is_k else '히라가나'
    jp = 'カタカナ' if is_k else 'ひらがな'
    fname = 'Appendix_Katakana.html' if is_k else 'Appendix_Hiragana.html'
    all_cells = []
    for rows in (SEION, DAKU, HANDAKU, YOON):
        for _, cells in rows:
            for c in cells:
                if c:
                    k, r = split(c)
                    all_cells.append((conv(k), r))
    if is_k:
        all_cells += GAIRAI
    data = json.dumps(all_cells, ensure_ascii=False)
    cards = [
        f'<div class="card"><div class="card-title">청음 (清音) — 기본 46자</div>{table(SEION, ["a", "i", "u", "e", "o"], conv)}</div>',
        '<div class="card"><div class="card-title">탁음 (濁音) · 반탁음 (半濁音)</div>'
        '<div class="appx-note">글자 오른쪽 위에 점 두 개(゛)를 찍으면 탁음, 동그라미(゜)를 찍으면 반탁음이 된다.</div>'
        f'{table(DAKU + HANDAKU, ["a", "i", "u", "e", "o"], conv)}</div>',
        '<div class="card"><div class="card-title">요음 (拗音)</div>'
        f'<div class="appx-note">い단 글자 뒤에 작은 <span lang="ja">{conv("ゃ・ゅ・ょ")}</span>를 붙여 한 박자로 읽는다.</div>'
        f'{table(YOON, ["ya", "yu", "yo"], conv)}</div>']
    if is_k:
        g = ''.join(cell_html(k, r) for k, r in GAIRAI)
        ex = ''.join(f'<tr><td class="jp-cell" lang="ja">{k}</td><td class="appx-ro">{r}</td><td>{m}</td></tr>'
                     for k, r, m in GAIRAI_EX)
        cards.append('<div class="card"><div class="card-title">외래어 표기 · 장음</div>'
                     '<div class="appx-note">외래어는 작은 <span lang="ja">ァ・ィ・ゥ・ェ・ォ</span>로 원래 소리를 나타낸다. '
                     '장음은 「<span lang="ja">ー</span>」로 쓰고 앞 모음을 길게 읽는다.</div>'
                     f'<div class="appx-grid">{g.replace("<td", "<div").replace("</td>", "</div>")}</div>'
                     '<table class="ref-table appx-ex"><thead><tr><th>단어</th><th>로마자</th><th>뜻</th></tr></thead>'
                     f'<tbody>{ex}</tbody></table></div>')
    else:
        cards.append('<div class="card"><div class="card-title">촉음 · 장음</div>'
                     '<div class="appx-note">작은 「<span lang="ja">っ</span>」는 다음 자음을 한 박자 쉬어 읽는다 '
                     '(<span lang="ja">きって</span> kitte 우표). 같은 모음이 이어지면 길게 읽는다 '
                     '(<span lang="ja">おかあさん</span> okāsan 어머니, <span lang="ja">とうきょう</span> Tōkyō 도쿄).</div></div>')
    quiz = ('<div class="card appx-quiz"><div class="card-title">읽기 연습</div>'
            '<div class="quiz-box"><div class="quiz-kana" lang="ja" id="qk"></div><div class="quiz-ro" id="qr"></div></div>'
            '<div class="appx-tools center"><button class="appx-btn" id="qshow">정답 보기</button>'
            '<button class="appx-btn primary" id="qnext">다음 글자</button></div>'
            '<div class="appx-note center">글자를 소리 내어 읽은 뒤 「정답 보기」로 확인한다. 위 표의 모든 글자에서 무작위로 나온다.</div></div>')
    tools = ('<div class="appx-tools sticky"><button class="appx-btn" id="toggle-ro">로마자 가리기</button>'
             '<span class="appx-hint">가린 상태에서 글자를 누르면 그 글자의 로마자만 보인다.</span></div>')
    js = ('<script>\nvar KANA=' + data + ''';
var tb=document.getElementById('toggle-ro');
tb.onclick=function(){var on=document.body.classList.toggle('hide-ro');tb.textContent=on?'로마자 보이기':'로마자 가리기';tb.classList.toggle('primary',on);
document.querySelectorAll('.kc.show').forEach(function(c){c.classList.remove('show');});};
document.querySelectorAll('.kc').forEach(function(c){c.onclick=function(){if(document.body.classList.contains('hide-ro'))c.classList.toggle('show');};});
var cur=null,qk=document.getElementById('qk'),qr=document.getElementById('qr');
function next(){var n;do{n=KANA[Math.floor(Math.random()*KANA.length)];}while(KANA.length>1&&n===cur);cur=n;qk.textContent=n[0];qr.textContent=n[1];qr.classList.remove('show');}
document.getElementById('qnext').onclick=next;document.getElementById('qshow').onclick=function(){qr.classList.add('show');};
next();
</script>''')
    html = ('<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">'
            '<link rel="stylesheet" href="assets/fonts.css" />\n<link rel="stylesheet" href="assets/session.css" />\n'
            '<link rel="stylesheet" href="assets/appendix.css" />\n'
            f'<title>부록 · {name} · 넥슨게임즈</title></head><body>\n'
            '<div class="topbar"><a href="index.html" onclick="if(window.parent!==window){window.parent.postMessage(\'showHome\',\'*\');return false;}">← 홈</a>'
            f'<span class="topbar-sep">|</span><span class="topbar-title">부록 · {name}</span></div>\n'
            '<div class="page">\n'
            f'<div class="page-header"><div class="date-badge">부록</div><h1><span lang="ja">{jp}</span> ({name})</h1>'
            f'<div class="subtitle">{name} 읽기 복습 · 넥슨게임즈 전화외국어 수업 · <span lang="ja">スクスク</span> 회화</div></div>\n'
            f'{tools}\n' + '\n'.join(cards) + f'\n{quiz}\n</div>\n{js}\n</body></html>\n')
    open(os.path.join(ROOT, fname), 'w', encoding='utf-8', newline='\n').write(html)
    print(fname, len(all_cells), 'kana')


if __name__ == '__main__':
    page('hira')
    page('kata')
