# helloAWS：Pythonではじめる2ページのサイト

大きな **helloAWS** と、小さな操作を楽しめるAWS学習用サイトです。

- `/`：名前を入れると、あいさつが変わるトップページ。
- `/learn`：AWSの仕組みの説明と、クリックして答えるミニクイズ。

Pythonの標準ライブラリだけで動きます。Flask、Docker、SAM CLI、Node.jsは不要です。
あいさつとクイズはブラウザー内のJavaScriptで動き、名前や回答をサーバーへ送信・保存しません。

## 1. ファイルを知ろう

編集するファイルは3つです。

```text
try1/
├── main.py        # Python本体。HTML・CSS・JavaScriptもここにまとめています
├── template.yaml  # CloudFormation：AWSの構成を記述
└── README.md      # この手順書
```

公開の準備をすると `.build/` が増えます。中身は自動生成されるので編集しません。
`requirements.txt` も `pip install` も不要です。

## 2. まずは自分のパソコンで開こう

以下は **WindowsのPowerShell** 用です。コードブロックの中だけを、順番にコピーして実行してください。
作業フォルダーが違う場合は、最初のパスを自分の保存先に置き換えます。

```powershell
cd C:\Users\kosuk\script\trainee\try1
python --version
```

Python 3.10以上が必要です。未インストールの場合は [Python公式サイト](https://www.python.org/downloads/windows/) からインストールし、PowerShellを開き直してください。
`python` が使えず `py` が使える場合は、このREADMEの `python` を `py` に読み替えます。

```powershell
python main.py
```

このPowerShellを開いたまま、ブラウザーで **http://localhost:8000** を開きます。

1. 大きな「helloAWS」が表示されることを確認。
2. 名前を入れて「あいさつする」を押す。Enterキーでも操作できます。
3. 「このサイトの仕組みを見る」を押して2ページ目へ。
4. クイズの選択肢を押して、メッセージが変わることを確認。
5. 確認が終わったら、PowerShellで **Ctrl+C** を押して終了。

ここまでAWSアカウントは不要で、AWSの料金も発生しません。
ローカルではPythonが直接リクエストを受けます。AWSへ公開すると、その入口がAPI Gatewayに変わります。

## 3. AWSでは何が動く？

```text
ブラウザー → API Gateway → Lambda（main.py）
ブラウザー ← API Gateway ← HTMLを返す
                              │
                              └→ CloudWatch Logs（実行ログ）

CloudFormation：上のAWSリソースとIAMロールを、YAMLからまとめて作る
S3：公開準備で作るPythonのZIPファイルを置く場所
```

| 用語 | このサイトでの役割 |
| --- | --- |
| CloudFormation | YAMLに書いた構成をAWS上に作るサービス |
| スタック | CloudFormationが作るリソースをまとめた単位。今回は `hello-aws` |
| API Gateway | HTTPSのURLを提供し、アクセスをLambdaに渡す入口 |
| Lambda | リクエストに応じてPythonを実行する場所 |
| IAMロール | Lambdaがログを書き込むための権限 |
| CloudWatch Logs | 実行エラーなどを調べるためのログ置き場 |
| S3バケット | デプロイするZIPファイルを保管する入れ物 |

EC2やデータベースは作りません。S3はコードの受け渡し用で、サイト本体の配信元はLambdaです。

## 4. AWSへ公開する前の準備

この先は自分のAWSアカウントにリソースを作ります。**公開URLは誰でも閲覧できます。**
学習用なので、個人情報や秘密情報はページに書かないでください。
API Gateway、Lambda、S3、ログには利用量に応じた料金が発生する場合があります。無料枠の適用はアカウントの条件で異なります。
料金が心配な場合は、AWSコンソールの「Billing and Cost Management」で予算通知も設定しておきましょう。予算通知は利用停止や料金上限の機能ではありません。

### 4-1. アカウントと操作権限

AWSアカウントを用意し、学習用のIAM Identity Centerユーザー、またはIAMユーザーで操作します。
日常の操作にはルートユーザーを使わないでください。

この手順にはCloudFormation、S3、Lambda、API Gateway、CloudWatch Logs、IAMロールの作成・削除、および `iam:PassRole` などの権限が必要です。
組織のアカウントなら、学習環境の利用可否と必要な権限を管理者に確認してください。

### 4-2. AWS CLIをインストール

[AWS公式のインストール手順](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) から **AWS CLI v2のWindows版** をインストールします。
PowerShellを開き直して確認します。

```powershell
aws --version
```

`aws-cli/2...` が出れば準備できています。

### 4-3. AWSへログイン

組織からIAM Identity Centerの開始URLを渡されている場合はこちらです。

```powershell
aws configure sso
aws sso login --profile 自分で設定したプロファイル名
$env:AWS_PROFILE = "自分で設定したプロファイル名"
```

`自分で設定したプロファイル名` は実際の名前に置き換えてください。

個人の学習アカウントでIAMユーザーのアクセスキーを使う場合は、代わりにこちらを実行します。

```powershell
aws configure
```

質問されたら、自分のアクセスキーID、シークレットアクセスキー、リージョン `ap-northeast-1`、出力形式 `json` を入力します。
アクセスキーはパスワードと同じように扱い、コードやREADME、Gitへ書き込まないでください。

どちらの場合も、操作先を確認します。

```powershell
aws sts get-caller-identity
```

表示された `Account` が、自分の学習用アカウントか確かめましょう。
このコマンドが失敗したら、認証を直してから次へ進んでください。

## 5. AWSへ公開しよう

**ここからは同じPowerShellで順番に実行します。各コマンドが成功してから次へ進んでください。**
最初のデプロイは数分かかることがあります。

### 5-1. 作業場所と名前を設定

```powershell
cd C:\Users\kosuk\script\trainee\try1
$region = "ap-northeast-1"
$stackName = "hello-aws"
$accountId = aws sts get-caller-identity --query Account --output text
if ($LASTEXITCODE -ne 0) { throw "AWSのログイン状態を確認してください" }
$bucketName = "hello-aws-code-$accountId-$([guid]::NewGuid().ToString('N').Substring(0, 12))"
$bucketName
```

`ap-northeast-1` は東京リージョンです。
バケット名は世界中で重複できないため、アカウントIDとランダムな文字を付けています。
**表示されたバケット名を控えておきましょう。後片付けで使います。**
以降は同じ `$region` を使います。

### 5-2. コードを置くS3バケットを作る（初回だけ）

```powershell
aws s3api create-bucket --bucket $bucketName --region $region --create-bucket-configuration LocationConstraint=$region
```

公開する必要がないので、公開アクセスを明示的にブロックします。

```powershell
aws s3api put-public-access-block --bucket $bucketName --region $region --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

このバケットはスタックの外で作ります。最後に手動で削除する手順も載せています。

### 5-3. main.pyだけをZIPにする

```powershell
New-Item -ItemType Directory -Force .build | Out-Null
python -m zipfile -c .build/function.zip main.py
```

これで `.build/function.zip` ができます。
ZIPの一番上に `main.py` が入るので、Lambdaが `main.lambda_handler` を見つけられます。
フォルダーごとZIPにすると場所がずれるので、このコマンドのまま作成してください。

### 5-4. コードをアップロードして、AWS用YAMLを生成

```powershell
aws cloudformation package --template-file template.yaml --s3-bucket $bucketName --s3-prefix hello-aws --output-template-file .build/packaged.yaml --region $region
```

このコマンドはZIPをS3へアップロードし、`Code: .build/function.zip` をS3の場所に置き換えた `.build/packaged.yaml` を作ります。
**元の `template.yaml` はローカルのZIPを指定したパッケージ前のテンプレートです。直接コンソールへアップロードせず、生成された `packaged.yaml` を使います。**
SAM変換は使わず、通常のCloudFormationで作成します。

### 5-5. YAMLを検証して、スタックを作成

```powershell
aws cloudformation validate-template --template-body file://.build/packaged.yaml --region $region
```

エラーが出なければ、デプロイします。

```powershell
aws cloudformation deploy --template-file .build/packaged.yaml --stack-name $stackName --capabilities CAPABILITY_IAM --region $region --no-fail-on-empty-changeset
```

`CAPABILITY_IAM` は「テンプレートに書かれたIAMロールの作成を認める」という指定です。
処理が成功するまで、このPowerShellを閉じずに待ちます。

### 5-6. 公開URLを表示

```powershell
aws cloudformation describe-stacks --stack-name $stackName --region $region --query "Stacks[0].Outputs[?OutputKey=='WebsiteUrl'].OutputValue" --output text
```

表示された `https://...execute-api.ap-northeast-1.amazonaws.com` のURLをブラウザーで開きます。
トップと「しくみ」の2ページ、あいさつ、クイズを試してみましょう。
AWSコンソールの「CloudFormation → hello-aws → 出力」からもURLを確認できます。

## 6. ページを変更してみよう

まずは `main.py` の `HOME` にある `hello<span>AWS</span>` や説明文を書き換えてみてください。

| main.pyの場所 | 変更する内容 |
| --- | --- |
| `STYLE` | 色、文字サイズ、余白などのCSS |
| `HOME` | トップページのHTMLとあいさつのJavaScript |
| `LEARN` | 2ページ目のHTMLとクイズのJavaScript |
| `render_page` | URLとページの対応 |
| `lambda_handler` | AWSからのアクセスを受け、HTTPレスポンスを返す処理 |
| `LocalHandler` | ローカルで同じ処理を試すための小さなサーバー |

ローカルは `Ctrl+C` で終了してから `python main.py` で起動し直し、ブラウザーを再読み込みします。
AWSへ反映するには **5-3 → 5-4 → 5-5の検証とデプロイ** をもう一度実行します。
同じスタック名とS3バケットを使えば、既存サイトが更新されます。コードが変わると `package` がS3の新しい保存先を生成するため、CloudFormationもコードの変更を認識します。

PowerShellを閉じた場合は、ログイン状態を確認し、以下の変数を設定し直してから更新してください。バケットを新しく作る必要はありません。

```powershell
$region = "ap-northeast-1"
$stackName = "hello-aws"
$bucketName = "初回に控えたバケット名"
```

## 7. うまくいかないとき

| 症状 | 確認すること |
| --- | --- |
| `python` / `aws` が見つからない | インストール後にPowerShellを開き直す。Pythonは `py --version` も試す |
| `Unable to locate credentials` / ログイン期限切れ | 手順4-3を確認。SSOなら `aws sso login --profile プロファイル名` を再実行 |
| `AccessDenied` | 操作先アカウントとIAM権限を確認。権限不足の操作名を管理者へ伝える |
| ZIPが見つからない | プロジェクトのフォルダーにいるか、5-3を実行したか確認 |
| `Code` の形式に関するエラー | 元のYAMLではなく、5-4で作った `.build/packaged.yaml` をデプロイする |
| ローカルの8000番ポートが使用中 | すでに起動している `python main.py` をCtrl+Cで止める |
| サイトで429が表示される | 学習用のAPI制限（目安：毎秒5リクエスト）です。少し待って再読み込み |
| サイトで500 / 502が表示される | 以下の手順でLambdaのログを確認 |
| 画面の変更が反映されない | ZIP作成・package・deployをすべてやり直し、ブラウザーを再読み込み |

デプロイ失敗時は、AWSコンソールの「CloudFormation → hello-aws → イベント」で失敗理由を確認します。
初回作成が `ROLLBACK_COMPLETE` になった場合は、原因を直し、手順8-1でスタックを削除してから再デプロイします。

Pythonのエラーログは、以下で確認できます（サイトにアクセスした後に実行）。

```powershell
$logGroup = aws cloudformation describe-stacks --stack-name $stackName --region $region --query "Stacks[0].Outputs[?OutputKey=='LogGroupName'].OutputValue" --output text
aws logs tail $logGroup --since 10m --region $region
```

ログは7日間保持します。API Gatewayのアクセスログは、この最小構成には含めていません。
リクエスト制限は料金の上限を保証するものではありません。

## 8. 勉強が終わったら削除しよう

### 8-1. サイトのスタックを削除

必要なコードは手元のファイルに残ります。AWS上のサイト、IAMロール、実行ログなどは削除されます。
PowerShellを開き直した場合は、先に以下の変数を設定します。

```powershell
$region = "ap-northeast-1"
$stackName = "hello-aws"
$bucketName = "初回に控えたバケット名"
```

```powershell
aws cloudformation delete-stack --stack-name $stackName --region $region
aws cloudformation wait stack-delete-complete --stack-name $stackName --region $region
```

成功すると公開URLにアクセスできなくなります。待機が失敗した場合は、コンソールのイベントで原因を確認してください。

### 8-2. コード用S3バケットも削除

**控えた名前が今回の学習専用バケットであることを確認してください。次のコマンドは中のZIPも削除します。**

```powershell
$bucketName
aws s3 ls "s3://$bucketName" --recursive --region $region
```

今回のコードだけが入ったバケットであると確認できたら、削除します。

```powershell
aws s3 rb "s3://$bucketName" --force --region $region
```

これで、今回作ったAWSリソースの後片付けは完了です。
手元の `.build/` は再生成できるファイルです。必要なければエクスプローラーで削除できます。

## 9. 公式ドキュメント

- [CloudFormation package：ローカルコードのアップロード](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/package.html)
- [CloudFormation：Lambda関数](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-lambda-function.html)
- [CloudFormation：HTTP API](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-apigatewayv2-api.html)
- [LambdaのPythonランタイム](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html)

このフォルダーには実装と手順を用意しています。AWSへの実デプロイ・課金・URL発行は、この手順を自分のアカウントで実行したときに行われます。
