"""2ページの学習サイト。ローカルでもAWS Lambdaでも同じページを返す。"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


# ファイルを増やさないため、共通の見た目もこのファイルにまとめています。
STYLE = """
:root { color-scheme: light; font-family: system-ui, sans-serif; color: #202b38;
  background: #faf8f3; }
* { box-sizing: border-box; }
body { margin: 0; }
a { color: inherit; }
header, main, footer { max-width: 1040px; margin: auto; padding: 24px; }
header { display: flex; align-items: center; justify-content: space-between;
  gap: 20px; border-bottom: 1px solid #deded7; }
.brand { font-weight: 800; text-decoration: none; letter-spacing: -.04em; }
nav { display: flex; gap: 20px; font-size: .9rem; }
nav a { text-underline-offset: 6px; }
nav a[aria-current="page"] { color: #a84800; font-weight: 700; }
main { min-height: 75vh; padding-top: 64px; padding-bottom: 64px; }
.eyebrow { color: #80552f; font-size: .8rem; letter-spacing: .16em; font-weight: 700; }
h1 { margin: 22px 0; font-size: clamp(4rem, 13vw, 9rem); line-height: 1.05;
  letter-spacing: -.075em; }
h1 span { color: #b95200; }
h2 { font-size: clamp(2rem, 6vw, 3.8rem); line-height: 1.2; letter-spacing: -.04em; }
p { line-height: 1.9; }
.intro { max-width: 620px; color: #56616b; }
.panel { background: white; border: 1px solid #deded7; border-radius: 20px;
  padding: 28px; margin: 30px 0; }
label { display: block; font-weight: 700; margin-bottom: 10px; }
.controls { display: flex; gap: 12px; flex-wrap: wrap; }
input { min-width: 0; max-width: 100%; border: 1px solid #91999f; border-radius: 9px;
  padding: 14px; font: inherit; background: white; color: #202b38; }
button, .button { display: inline-block; border: 0; border-radius: 9px;
  background: #243344; color: white; padding: 14px 22px; cursor: pointer;
  font: inherit; text-decoration: none; font-weight: 700; }
button:hover, .button:hover { background: #43566c; }
:focus-visible { outline: 3px solid #b95200; outline-offset: 4px; }
.result { min-height: 2em; margin-bottom: 0; color: #80552f; font-weight: 700; }
.flow { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin: 24px 0; }
.flow article { background: white; border: 1px solid #deded7; border-radius: 14px;
  padding: 22px; }
.flow small { color: #80552f; }
.flow h3 { margin-bottom: 6px; }
.flow p { font-size: .9rem; color: #56616b; }
footer { border-top: 1px solid #deded7; color: #59616a; font-size: .8rem; }
@media (max-width: 600px) {
  .flow { grid-template-columns: 1fr; }
  main { padding-top: 36px; }
  .panel { padding: 20px; }
  .controls input { width: 100%; }
}
"""

HOME = """
<p class="eyebrow">MY FIRST CLOUD / 01</p>
<h1>hello<span>AWS</span></h1>
<p class="intro"> <br>
Pythonでつくったサイトを、AWSの上で動かしてみよう。</p>
<section class="panel" aria-label="あいさつを試す">
  <form id="greeting-form">
    <label for="name">あなたの名前で、hello。</label>
    <div class="controls">
      <input id="name" name="name" placeholder="例：じろう" maxlength="30" autocomplete="given-name">
      <button type="submit">あいさつする →</button>
    </div>
  </form>
  <p id="greeting" class="result" role="status">名前を入れて、ボタンを押してみよう。</p>
</section>
<a class="button" href="/learn">このサイトの仕組みを見る ↗</a>
<script>
document.getElementById('greeting-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const name = document.getElementById('name').value.trim() || 'AWS';
  document.getElementById('greeting').textContent = `hello ${name}！ クラウドへようこそ。`;
});
</script>
"""

LEARN = """
<p class="eyebrow">HOW IT WORKS / 02</p>
<h2>このページが届くまで。</h2>
<p class="intro">AWSに公開すると、3つのステップでページが届きます。<br>
CloudFormationは、この仕組みをYAMLからまとめて作ります。</p>
<div class="flow">
  <article><small>01 / REQUEST</small><h3>ブラウザー</h3>
    <p>あなたがURLを開くと、「ページをください」というリクエストが送られます。</p></article>
  <article><small>02 / ENTRANCE</small><h3>API Gateway</h3>
    <p>インターネットからの入口。リクエストをLambdaへ届けます。</p></article>
  <article><small>03 / PYTHON</small><h3>Lambda</h3>
    <p>main.pyを実行し、HTMLを返します。API Gatewayを通ってブラウザーに届きます。</p></article>
</div>
<section class="panel" data-quiz aria-labelledby="quiz-title"
  data-explanation="LambdaがPythonを実行して、ページを返します。"
  data-hint="API Gatewayは入口、CloudFormationは構成を作る係です。">
  <h3 id="quiz-title">ミニクイズ 1 / 5：Pythonを実行するのは？</h3>
  <div class="controls">
    <button type="button" data-answer="wrong">API Gateway</button>
    <button type="button" data-answer="correct">Lambda</button>
    <button type="button" data-answer="wrong">CloudFormation</button>
  </div>
  <p id="answer" class="result" role="status">答えを選んでみよう。</p>
</section>
<section class="panel" data-quiz aria-labelledby="quiz-title-2"
  data-explanation="S3はファイルを保管するサービス。このサイトではPythonのZIPを置きます。"
  data-hint="ZIPなどのファイルを保管するサービスを選んでみよう。">
  <h3 id="quiz-title-2">ミニクイズ 2 / 5：PythonのZIPを保管するのは？</h3>
  <div class="controls">
    <button type="button" data-answer="correct">S3</button>
    <button type="button" data-answer="wrong">CloudWatch Logs</button>
    <button type="button" data-answer="wrong">API Gateway</button>
  </div>
  <p class="result" role="status">答えを選んでみよう。</p>
</section>
<section class="panel" data-quiz aria-labelledby="quiz-title-3"
  data-explanation="API GatewayがHTTPSの入口になり、リクエストをLambdaへ渡します。"
  data-hint="ブラウザーから届くリクエストの入口を選んでみよう。">
  <h3 id="quiz-title-3">ミニクイズ 3 / 5：ブラウザーからのアクセスを受け付ける入口は？</h3>
  <div class="controls">
    <button type="button" data-answer="wrong">S3</button>
    <button type="button" data-answer="wrong">CloudFormation</button>
    <button type="button" data-answer="correct">API Gateway</button>
  </div>
  <p class="result" role="status">答えを選んでみよう。</p>
</section>
<section class="panel" data-quiz aria-labelledby="quiz-title-4"
  data-explanation="CloudFormationは、YAMLに書いたAWSリソースをスタックとしてまとめて作ります。"
  data-hint="template.yamlをアップロードして使うサービスを思い出してみよう。">
  <h3 id="quiz-title-4">ミニクイズ 4 / 5：YAMLからAWSの構成をまとめて作るのは？</h3>
  <div class="controls">
    <button type="button" data-answer="wrong">Lambda</button>
    <button type="button" data-answer="correct">CloudFormation</button>
    <button type="button" data-answer="wrong">S3</button>
  </div>
  <p class="result" role="status">答えを選んでみよう。</p>
</section>
<section class="panel" data-quiz aria-labelledby="quiz-title-5"
  data-explanation="CloudWatch LogsでLambdaの実行ログを確認し、エラーの原因を調べられます。"
  data-hint="Pythonのエラーメッセージなど、実行ログを保存するサービスを選んでみよう。">
  <h3 id="quiz-title-5">ミニクイズ 5 / 5：Pythonの実行エラーをログで調べるのは？</h3>
  <div class="controls">
    <button type="button" data-answer="wrong">API Gateway</button>
    <button type="button" data-answer="wrong">S3</button>
    <button type="button" data-answer="correct">CloudWatch Logs</button>
  </div>
  <p class="result" role="status">答えを選んでみよう。</p>
</section>
<a href="/">← helloAWSに戻る</a>
<script>
// 問題ごとに処理することで、押した問題の答えだけを更新します。
document.querySelectorAll('[data-quiz]').forEach((quiz) => {
  quiz.querySelectorAll('[data-answer]').forEach((button) => {
    button.addEventListener('click', () => {
      quiz.querySelector('.result').textContent = button.dataset.answer === 'correct'
        ? `正解！ ${quiz.dataset.explanation}`
        : `もう一度！ ${quiz.dataset.hint}`;
    });
  });
});
</script>
"""


def render_page(path):
    """URLに応じて、HTTPステータスとHTMLを返す。"""
    if path == "/":
        title, content, status = "helloAWS", HOME, 200
    elif path in ("/learn", "/learn/"):
        title, content, status = "しくみ | helloAWS", LEARN, 200
    else:
        title, content, status = (
            "ページがありません | helloAWS",
            '<h2>404</h2><p>ページが見つかりません。</p><a href="/">トップへ戻る</a>',
            404,
        )

    home_current = 'aria-current="page"' if path == "/" else ""
    learn_current = 'aria-current="page"' if path in ("/learn", "/learn/") else ""
    html = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="PythonとCloudFormationではじめる、小さなAWS学習サイト。">
  <title>{title}</title>
  <style>{STYLE}</style>
</head>
<body>
  <header>
    <a class="brand" href="/">helloAWS<span aria-hidden="true"> ↗</span></a>
    <nav aria-label="メインメニュー">
      <a href="/" {home_current}>ホーム</a>
      <a href="/learn" {learn_current}>しくみ</a>
    </nav>
  </header>
  <main>{content}</main>
  <footer>helloAWS — 小さくつくって、動かして学ぶ。</footer>
</body>
</html>"""
    return status, html


def lambda_handler(event, context):
    """API Gateway（HTTP API / payload v2）から呼ばれるAWS用の入口。"""
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    if method not in ("GET", "HEAD"):
        return {"statusCode": 405, "headers": {"Allow": "GET, HEAD"}, "body": "Method Not Allowed"}

    status, html = render_page(event.get("rawPath", "/"))
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
        "body": "" if method == "HEAD" else html,
    }


class LocalHandler(BaseHTTPRequestHandler):
    """ローカルのHTTPリクエストをLambdaと同じ処理へ渡す。"""

    def do_GET(self):
        response = lambda_handler(
            {
                "rawPath": urlsplit(self.path).path,
                "requestContext": {"http": {"method": self.command}},
            },
            None,
        )
        body = response["body"].encode("utf-8")
        self.send_response(response["statusCode"])
        for name, value in response["headers"].items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_HEAD = do_GET


if __name__ == "__main__":
    print("ブラウザーで http://localhost:8000 を開いてください。終了: Ctrl+C", flush=True)
    server = ThreadingHTTPServer(("127.0.0.1", 8000), LocalHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nサーバーを終了しました。")
    finally:
        server.server_close()
