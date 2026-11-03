# helloAWS：AWSコンソールで公開する、はじめてのPythonサイト

**AWSコンソールへのログインができているところから始めます。AWSへの操作はすべてブラウザーで行います。**
AWS CLIのインストール、アクセスキーの発行、コマンドでのデプロイは不要です。

作るのは、小さな2ページのサイトです。

- **ホーム `/`**：大きな「helloAWS」と、名前を入力してあいさつを変えるボタン。
- **しくみ `/learn`**：AWSの仕組みの説明と、クリックして答えるミニクイズ。

あいさつとクイズはブラウザーの中で動きます。入力した名前や回答はサーバーに送信・保存しません。
Pythonの外部ライブラリは不要です。

## 1. 最初に、今日の流れを確認

```text
① パソコンにファイルを用意
② S3に「ZIPの置き場」を作る
③ function.zipをS3へアップロード
④ CloudFormationにtemplate.yamlを渡す
⑤ S3のバケット名とZIP名を入力して作成
⑥ 表示されたURLをブラウザーで開く
```

CloudFormationとは、**YAMLという設定ファイルを読んで、AWSの構成をまとめて作るサービス**です。
この手順ではLambdaやAPI Gatewayをそれぞれ手作業で作る必要はありません。

| ファイル | 役割 | どこにアップロードする？ |
| --- | --- | --- |
| `main.py` | ページを作るPython本体。見た目とボタンの処理も入っています | ZIPの中に入れます |
| `function.zip` | `main.py`だけを入れた、用意済みのアップロード用ZIP | S3 |
| `template.yaml` | 作るAWSリソースを書いたCloudFormationの設計図 | CloudFormation |
| `README.md` | この手順書 | アップロードしません |

編集するファイルは `main.py` と `template.yaml`、このREADMEです。`function.zip` はPythonを梱包したものです。

## 2. パソコンにファイルを用意

### 2-1. このフォルダーが手元にある場合

エクスプローラーで `C:\Users\kosuk\script\trainee\try1` を開きます。
**`function.zip` と `template.yaml` が見えること**を確認できれば、手順3へ進んでください。
初回用のZIPは作成済みなので、自分で圧縮し直す必要はありません。

### 2-2. GitHubからダウンロードする場合

1. [GitHubリポジトリ](https://github.com/kosukechun/try01) を開きます。
2. 緑色の **「Code」→「Download ZIP」** を押します。
3. ダウンロードした `try01-main.zip` を右クリックし、**「すべて展開」→「展開」** を押します。
4. 展開されたフォルダーを開き、`function.zip` と `template.yaml` を確認します。

**S3にアップロードするのは、中に入っている `function.zip` です。**
GitHubからダウンロードしたフォルダー全体のZIP `try01-main.zip` を、そのままアップロードしないでください。

### 2-3. 拡張子を見えるようにする

`.py`、`.zip`、`.yaml` の部分を「拡張子」といいます。見えるようにするとファイルを間違えにくくなります。

- Windows 11：エクスプローラー上部の **「表示」→「表示」→「ファイル名拡張子」** をオン。
- Windows 10：エクスプローラー上部の **「表示」→「ファイル名拡張子」** をオン。

ファイル名が `template.yaml.txt` になっていないことも確認します。

## 3. AWSコンソールの場所を確認

### 3-1. 東京リージョンを選ぶ

1. ログイン済みのAWSコンソールを開きます。
2. 画面上部の **リージョン名** を押します。
3. **「アジアパシフィック（東京） / ap-northeast-1」** を選びます。

リージョンは、AWSのリソースを置く地域です。
**この手順では、S3バケットもCloudFormationスタックも東京で作ります。**
サービスを切り替えたときも東京か確認してください。S3の一覧画面は複数の地域を表示することがあるので、バケット作成画面のリージョンも確認します。

### 3-2. サービスを開く方法

画面上部の検索欄に `S3` や `CloudFormation` と入力し、検索結果のサービス名を押します。
左側のメニューが隠れているときは、左上の **「≡」** を押すと開けます。
画面の言語や更新によって表記が少し違うため、主なボタンには英語名も併記しています。

### 3-3. 費用と権限

公開すると、**URLを知っている人は誰でもサイトを閲覧できます。** ページに秘密情報は書かないでください。
Lambda、API Gateway、S3、ログなどは利用量に応じて料金が発生する場合があります。無料枠の条件はアカウントによって異なります。
学習後は手順10で削除します。

操作にはS3、CloudFormation、Lambda、API Gateway、CloudWatch Logs、IAMロールの作成・削除や `iam:PassRole` などの権限が必要です。
ログインできていても権限不足で `AccessDenied` になる場合は、組織の管理者へエラーに出た操作名を伝えてください。

## 4. S3にZIPの置き場を作る

S3はファイルを保管するサービスです。その入れ物を **「バケット」** と呼びます。
ここで作るバケットは今回の学習専用にします。

1. 上部の検索欄で **`S3`** を検索して開きます。
2. 左側の **「汎用バケット（General purpose buckets）」** または **「バケット（Buckets）」** を開きます。
3. **「バケットを作成（Create bucket）」** を押します。
4. 以下の表に合わせて入力・確認します。

| 項目 | 設定 |
| --- | --- |
| AWSリージョン | **アジアパシフィック（東京） / ap-northeast-1** |
| バケットタイプ（表示される場合） | **汎用（General purpose）** |
| バケット名 | 自分だけの名前。例：`hello-aws-code-20261103-a7c92d` |
| オブジェクト所有者 | **ACL無効（推奨）** のまま |
| パブリックアクセスをすべてブロック | **チェックを付けたまま** |
| バケットのバージョニング | **無効** のまま |
| デフォルトの暗号化 | **Amazon S3マネージドキーを使用したサーバー側の暗号化（SSE-S3）** |
| その他 | 初期設定のまま |

5. 画面下部の **「バケットを作成」** を押します。
6. 作成したバケット名をメモします。後で `CodeBucketName` に入力します。

名前が他の利用者と重複すると作成できません。「既に存在します」と表示されたら、末尾の英数字を自分で変えて再試行します。
小文字の英数字とハイフンで名前を付けると分かりやすいです。

**このバケットを公開する設定や、静的ウェブサイトホスティングの設定は不要です。**
サイトの入口はAPI Gatewayで、S3はコードの保管場所として使います。[AWS公式のS3入門](https://docs.aws.amazon.com/AmazonS3/latest/userguide/GetStartedWithS3.html)

## 5. function.zipをS3にアップロード

1. S3の一覧から、今作ったバケット名を押します。
2. **「オブジェクト（Objects）」** タブを開きます。
3. **「アップロード（Upload）」** を押します。
4. **「ファイルを追加（Add files）」** を押します。
5. パソコンの **`function.zip`** を選び、「開く」を押します。
6. アップロード一覧に `function.zip` が1つ表示されていることを確認します。
7. 設定は変更せず、画面下部の **「アップロード」** を押します。
8. 成功の表示を確認して、「閉じる」を押します。
9. バケットのオブジェクト一覧に `function.zip` があることを確認します。

今回はフォルダーを作らず、バケット直下へZIPを置きます。
S3上のファイルの場所を **「オブジェクトキー」** と呼び、この場合は `function.zip` です。

ここで、次の2つを控えます。

| 控えるもの | 入力例 |
| --- | --- |
| バケット名 | `hello-aws-code-20261103-a7c92d` ※自分で作った実際の名前 |
| オブジェクトキー | `function.zip` |

オブジェクト名を押すと詳細を確認できます。フォルダーの中に置いた場合、キーには `code/function.zip` のようにフォルダー部分も含まれます。
S3のオブジェクトURLを開いて `AccessDenied` になっても、非公開設定なら自然な動作です。公開設定へ変更する必要はありません。[AWS公式のアップロード手順](https://docs.aws.amazon.com/AmazonS3/latest/userguide/upload-objects.html)

## 6. CloudFormationでサイトを作る

### 6-1. スタックの作成画面へ

1. 上部の検索欄で **`CloudFormation`** を検索して開きます。
2. リージョンが **東京** であることを確認します。
3. 左メニューの **「スタック（Stacks）」** を開きます。
4. **「スタックの作成（Create stack）」** を押します。
5. 選択肢が出た場合は **「新しいリソースを使用（標準） / With new resources (standard)」** を選びます。

スタックは「このYAMLから作るAWSリソース一式」のまとまりです。

### 6-2. template.yamlをアップロード

1. **「テンプレートの準備」** で **「既存のテンプレートを選択（Choose an existing template）」** を選びます。
2. **「テンプレートの指定」** で **「テンプレートファイルのアップロード（Upload a template file）」** を選びます。
3. **「ファイルの選択（Choose file）」** を押します。
4. パソコンの **`template.yaml`** を選びます。
5. ファイル名やアップロード先のS3 URLが表示されたら、**そのS3 URLもメモしてから**「次へ（Next）」を押します。後片付けで使います。

**ここで選ぶのはYAMLです。`function.zip` や `main.py` は選びません。**
このYAMLはコンソールに直接アップロードできます。変換や編集は不要です。[CloudFormation公式の作成手順](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html)

### 6-3. スタック名とパラメーターを入力

「スタックの詳細を指定」という画面で、次のように入力します。

| 項目 | 入力する値 |
| --- | --- |
| スタック名（Stack name） | **`hello-aws`** |
| `CodeBucketName` | **手順4で作ったバケット名** |
| `CodeObjectKey` | **`function.zip`**（初期値のまま） |

`CodeBucketName` は例をそのまま使わず、自分の実際の名前を入力します。
`s3://`、`https://`、`/function.zip` は付けません。

```text
CodeBucketName : hello-aws-code-20261103-a7c92d  ← 自分のバケット名に置き換える
CodeObjectKey  : function.zip
```

入力できたら **「次へ」** を押します。

### 6-4. オプションを確認

「スタックオプションの設定」では、タグ、アクセス許可用の既存IAMロールなどは初期設定のまま進めます。
この学習用に、既存のロールを新しく選ぶ必要はありません。

**「このテンプレートによってIAMリソースが作成される場合があることを承認します」**
（`I acknowledge that AWS CloudFormation might create IAM resources`）というチェックが表示されたら、内容を確認してオンにします。

これは、Lambdaが実行ログを書き込むためのIAMロールをYAMLから作ることへの確認です。
画面の版によって、このチェックは最後の確認画面に表示されることもあります。
**「次へ」** を押します。

### 6-5. 作成を開始

1. 最後の確認画面で、スタック名が `hello-aws` になっていることを確認します。
2. `CodeBucketName` と `CodeObjectKey` の入力ミスがないか確認します。
3. IAMリソースの承認チェックが最後に表示される場合はオンにします。
4. **「送信（Submit）」または「スタックの作成（Create stack）」** を押します。
5. 「イベント（Events）」タブで進行状況を確認します。更新ボタンで表示を更新できます。

| 状態 | 意味 |
| --- | --- |
| `CREATE_IN_PROGRESS` | 作成中。数分待ちます |
| **`CREATE_COMPLETE`** | 作成成功。次へ進めます |
| `CREATE_FAILED` | いずれかの作成が失敗。手順9で理由を確認します |
| `ROLLBACK_IN_PROGRESS` | 失敗した作成を取り消している途中 |
| `ROLLBACK_COMPLETE` | 取り消し完了。成功ではありません |

処理中に同じスタックを何度も作り直す必要はありません。まず結果を待ちます。

### 6-6. 公開URLを開く

1. `hello-aws` の状態が **`CREATE_COMPLETE`** になったら、スタックを選びます。
2. **「出力（Outputs）」** タブを開きます。
3. キーが **`WebsiteUrl`** の行を探します。
4. 値にある `https://...execute-api.ap-northeast-1.amazonaws.com` をコピーします。
5. ブラウザーの新しいタブのアドレス欄に貼り付けて開きます。

表示できたら、次を試します。

- 大きな「helloAWS」が見える。
- 名前を入力して「あいさつする」を押すと、表示が変わる。
- 「このサイトの仕組みを見る」で2ページ目に移動できる。
- クイズの選択肢を押すと答え合わせが表示される。
- 「helloAWSに戻る」でホームに戻れる。

ここまでできれば公開完了です。`localhost` のURLとは別に、AWS上のURLができました。
手元のPythonサーバーを止めても、AWS上のサイトは動作します。

## 7. どんな構成ができた？

```text
ブラウザー → API Gateway → Lambda（main.py）
ブラウザー ← API Gateway ← HTMLを返す
                              │
                              └→ CloudWatch Logs（実行ログ）

S3：PythonのZIPを保管する場所
CloudFormation：YAMLから上の構成とIAMロールをまとめて作る係
```

CloudFormationの **「リソース（Resources）」** タブで、作成したリソースを確認できます。
テンプレート内の名前を「論理ID」、実際にAWSに付いた名前を「物理ID」といいます。

| 論理ID | 役割 |
| --- | --- |
| `WebsiteFunction` | Pythonを実行するLambda関数 |
| `WebsiteApi` | HTTPSの入口となるAPI Gateway |
| `WebsiteIntegration` | API GatewayとLambdaの接続 |
| `WebsiteRoute` | 受け取ったURLをLambdaへ渡すルール |
| `WebsiteStage` | APIを公開するための設定 |
| `WebsiteInvokePermission` | このAPIからLambdaを呼び出せるようにする許可 |
| `WebsiteRole` | Lambdaにログ書き込み権限を渡すIAMロール |
| `WebsiteLogs` | 7日間の実行ログを保存する場所 |

手動で作ったコード用S3バケットは、このスタックの管理対象に含まれません。
EC2やデータベースは作りません。

## 8. ページを変更して、再アップロードする

### 8-1. main.pyを編集

例えば、`main.py` の `HOME` にある `hello<span>AWS</span>` や説明文を書き換えて保存します。

| main.pyの場所 | 変更する内容 |
| --- | --- |
| `STYLE` | 色、文字サイズ、余白などのCSS |
| `HOME` | トップページのHTMLとあいさつのJavaScript |
| `LEARN` | 2ページ目のHTMLとクイズのJavaScript |
| `render_page` | URLとページの対応 |
| `lambda_handler` | AWSからのアクセスを受け、ページを返すPythonの入口 |
| `LocalHandler` | パソコンだけで試すためのサーバー |

### 8-2. 新しいZIPをエクスプローラーで作る

1. **`main.py` ファイルだけ**を選んで右クリックします。親フォルダーは選びません。
2. Windows 11では **「ZIPファイルに圧縮する」** または **「圧縮先 → ZIPファイル」** を選びます。
3. メニューにない場合やWindows 10では、**「その他のオプションを確認 → 送る → 圧縮（zip形式）フォルダー」** を選びます。Windows 10は「送る」からでかまいません。
4. 作成されたZIPの名前を **`function-v2.zip`** に変更します。
5. ZIPをダブルクリックし、開いた直後に **`main.py`** が見えることを確認します。

正しい中身は次の形です。READMEやYAMLをZIPに入れる必要はありません。

```text
function-v2.zip
└── main.py
```

次のように親フォルダーが入っていると、LambdaがPythonの入口を見つけられません。

```text
function-v2.zip
└── try1/
    └── main.py
```

### 8-3. S3に新しいZIPをアップロード

1. S3を開き、最初に作ったコード用バケットを選びます。
2. 手順5と同じように **`function-v2.zip`** をアップロードします。
3. オブジェクト一覧に、新しい名前のZIPがあることを確認します。

**更新するたびに `function-v2.zip`、`function-v3.zip` のように名前を変えます。**
同じ `function.zip` を上書きするだけでは、CloudFormationはコードの変更を自動検知しません。
ZIPのキーかバージョンを変更する必要があるため、この手順では名前を変えます。[AWS公式の説明](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-lambda-function-code.html)

### 8-4. CloudFormationを更新

1. CloudFormationを東京リージョンで開き、**`hello-aws`** を選びます。
2. **「更新（Update）」** を押します。方式を選ぶ画面が出たら、通常の **「直接更新（Direct update）」** に進みます。
3. Pythonの内容だけを変更した場合は **「既存のテンプレートを使用（Use existing template）」** を選び、「次へ」を押します。
4. `CodeBucketName` は変更しません。
5. `CodeObjectKey` の **「既存の値を使用」** が表示される場合はオフにし、**`function-v2.zip`** に変更します。
6. オプションはそのまま「次へ」で進み、IAMリソースの承認が表示されたら確認します。
7. 最後に **「送信（Submit）」** を押します。
8. **`UPDATE_COMPLETE`** になるまで待ちます。
9. 公開URLを再読み込みし、変更が反映されたことを確認します。

YAML自体も編集した場合は、手順3で **「既存のテンプレートを置換（Replace existing template）」→「テンプレートファイルのアップロード」** を選び、更新した `template.yaml` を指定します。[AWS公式のスタック更新手順](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-direct.html)

## 9. うまくいかないとき

### 9-1. スタック作成・更新が失敗した

1. CloudFormationで `hello-aws` を開きます。
2. **「イベント（Events）」** タブを開きます。
3. `CREATE_FAILED` または `UPDATE_FAILED` の行を探します。
4. **「ステータスの理由（Status reason）」** を読みます。列が見切れる場合は横へスクロールします。

| 表示・症状 | 確認すること |
| --- | --- |
| `NoSuchBucket` | `CodeBucketName` と、実際のS3バケット名が一致しているか |
| `NoSuchKey` | `CodeObjectKey` とS3上のキーが一致しているか。大文字・小文字やフォルダー名も確認 |
| リージョンに関するエラー | S3バケットとCloudFormationが両方とも東京か |
| `AccessDenied` | 自分の権限、バケットの所有アカウントを確認。組織なら管理者へエラーを共有 |
| IAMリソース作成の承認を求められる | オプションまたは確認画面のIAM承認チェックをオンにする |
| パラメーターが表示されない | このリポジトリの最新版の `template.yaml` を選んだか |
| `No updates are to be performed` | 新しいZIPを別名でS3へ置き、`CodeObjectKey` も新しい名前にしたか |
| `ROLLBACK_COMPLETE` | 初回作成の取り消し完了。理由を直し、失敗したスタックを削除してから手順6をやり直す |

失敗したスタックを削除するときも、対象が今回の `hello-aws` であることを確認します。
コード用S3バケットが正常なら、初回作成失敗のたびに作り直す必要はありません。
更新が `UPDATE_ROLLBACK_COMPLETE` で終わった場合は、以前の構成に戻った状態です。原因を直し、同じスタックで更新をやり直します。

### 9-2. URLを開くと500 / 502になる

Lambdaのログをコンソールから確認します。

1. CloudFormationの `hello-aws` で **「出力（Outputs）」** を開きます。
2. **`LogGroupName`** の値をコピーしておきます。
3. 上部検索で **`CloudWatch`** を検索して開きます。リージョンは東京です。
4. 左側の **「ログ（Logs）」→「ロググループ（Log groups）」** を開きます。
5. 検索欄で、先ほどの `LogGroupName` を探して開きます。
6. **「ログストリーム（Log streams）」** で、最終イベント時刻が新しいものを開きます。
7. `ERROR` や `Traceback` の近くにあるメッセージを確認します。

`Unable to import module 'main'` と出た場合、ZIPの一番上に `main.py` が入っているか確認します。
`main.py.txt` になっている場合も読み込めません。正しいZIPを別名で作り直し、手順8で更新します。
構文エラーは、メッセージに表示された `main.py` の行番号を見て修正します。
ログがない場合は公開URLへもう一度アクセスしてから、ログ画面を更新してください。

### 9-3. その他のよくある症状

| 症状 | 確認すること |
| --- | --- |
| バケット名が既に使われている | 末尾の英数字を変えて、別名で作成 |
| S3のURLが `AccessDenied` | S3は非公開で正常。公開サイトはCloudFormationの `WebsiteUrl` を開く |
| 作ったスタックが見えない | CloudFormationのリージョンが東京か、表示フィルターで隠れていないか |
| ページが404になる | まず `WebsiteUrl` の値そのものを開く。2ページ目は末尾に `/learn` |
| サイトで429が出る | APIのリクエスト制限です。少し待って再読み込み |
| ページが更新されない | `UPDATE_COMPLETE` か、ZIPの中身は新しいか、キーも変更したか確認 |

ログは7日間保存します。API Gatewayのアクセスログは、この最小構成には含めていません。
APIには学習用の制限（目安：毎秒5リクエスト）を設けていますが、料金上限を保証する機能ではありません。

## 10. 勉強が終わったら、コンソールで削除

**今回作った学習用のものだけを削除します。削除したAWSリソースやログは元に戻せません。**
パソコンとGitHubにあるPython・YAMLは残るので、必要なときに作り直せます。

### 10-1. CloudFormationのスタックを削除

1. CloudFormationを東京リージョンで開きます。
2. 一覧から **`hello-aws`** を選びます。
3. **「削除（Delete）」** を押します。
4. 確認画面で対象名を確認し、削除を実行します。
5. `DELETE_IN_PROGRESS` の間は待ちます。
6. `DELETE_COMPLETE` になるか、通常の一覧から消えたら完了です。

Lambda、API Gateway、IAMロール、ロググループなど、スタック内のリソースが削除されます。
削除済みのスタックが見たい場合は、一覧の表示フィルターを「削除済み」に切り替えます。
`DELETE_FAILED` がある場合は「イベント」で理由を確認してください。

### 10-2. コード用S3バケットを空にして削除

**S3バケットは手動で作ったので、スタックを消しても残ります。**

1. S3を開き、手順4で作った **自分の学習専用バケット** を選択します。
2. 中身が今回の `function.zip`、`function-v2.zip` などであることを確認します。
3. 一覧の **「空にする（Empty）」** を押します。
4. 確認画面の指示どおりの文字列を入力し、**「空にする」** を実行します。
5. オブジェクトの削除完了を確認して、バケット一覧へ戻ります。
6. 同じバケットを選び、**「削除（Delete）」** を押します。
7. 確認画面にバケット名を入力し、削除します。

### 10-3. YAML用のS3ファイルも確認

手順6でYAMLを直接アップロードすると、CloudFormationがテンプレート保管用のS3バケットを自動作成することがあります。
このバケットとYAMLは、スタック削除後も残ります。

- バケット名は `cf-templates-` で始まる場合があります。
- 手順6-2で控えたテンプレートのS3 URLから、保存先のバケットとオブジェクトを確認できます。
- 片付ける場合は、S3で **今回の `template.yaml` に対応するオブジェクトだけ** を確認して削除します。
- 他のスタックのテンプレートが入っている可能性があるため、共有バケットを一括で空にしないでください。
- 今回だけのために作られた空のバケットであると確認できる場合は、バケットも削除できます。

保管場所の仕組みは [CloudFormation公式ドキュメント](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html) に記載されています。

## 11. おまけ：AWSへ上げる前に、ローカルで試す

AWSへの公開操作にはコマンドを使いません。ここは、パソコンだけで動かす場合の任意の手順です。
Python 3.10以上が入っている環境で、PowerShellを開きます。

```powershell
cd C:\Users\kosuk\script\trainee\try1
python main.py
```

ブラウザーで **http://localhost:8000** を開きます。
`python` が使えず `py` が使える場合は `py main.py` とします。
終了するときは、このPowerShellで **Ctrl+C** を押します。
Pythonを編集したときは、停止してから起動し直してください。

## 動作確認の範囲

ローカルでのHTTP応答と、あいさつ・クイズの処理を確認しています。
ZIPにはルート直下の `main.py` だけを格納しています。
このフォルダーの作成・更新時に、AWSへの実デプロイは行っていません。AWS上のリソース作成と公開URLの発行は、このREADMEを実行したときに行われます。
