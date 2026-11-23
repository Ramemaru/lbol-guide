# LBoL 攻略ノート — 編集画面付き

LBoL（東方光耀夜）の上級者向け、個人考察・攻略サイトの初期版です。
カード・ボスの**個別記事**を中心に、キャラ別攻略は後から充実させる方針です。
**見本記事は実際の攻略データではありません。**

## できること

- サイト：カード解説／ボス攻略／キャラ別攻略の記事一覧・個別ページ・検索・絞り込み
- 管理画面：`/admin/` からカード・ボス・キャラ記事の作成・編集・削除
- 記事：タイトル、短い説明、タグ、考察の確信度、バージョン、更新日、Markdown本文
- 画像：記事の代表画像と本文中の画像をアップロード可能
- 公開制御：**「下書き」をONにした記事は公開サイトには表示しない**（新規作成時はON）
- 公開後：管理画面で保存 → GitHub にコミット → Netlify が自動でサイトを更新

記事は `content/cards/`, `content/bosses/`, `content/characters/` の Markdown ファイルで管理します。データベースは不要です。

**公開の最短手順は [SETUP.md](SETUP.md) にまとめています。**

## まずサイトを見たい

`dist/index.html` をブラウザで開くと、記事一覧などの**閲覧**ができます。ローカルファイルをダブルクリックしても記事リンクは移動できます。**編集画面はHTMLを直接開くだけでは使えません**。

## 自分のPCで編集してみる（公開前でも可）

1. [Python 3.10以降](https://www.python.org/downloads/) と [Node.js 20以降](https://nodejs.org/) を用意する。
2. Windows は `start-editor.bat` をダブルクリック。初回だけ必要なライブラリがダウンロードされます。
3. ブラウザに `http://127.0.0.1:8000/admin/` が自動で開きます。
4. 「カード解説」または「ボス攻略」を選び、見本を編集／「新規作成」で記事を追加します。
5. **下書きのチェックを外して**保存すれば、サイト側に表示する記事になります。`http://127.0.0.1:8000/` を再読み込みしてください。

編集したMarkdownは手元の `content/` に残ります。ローカルモードにはログインが不要です。ローカル編集サーバーは自分のPC（127.0.0.1）だけで待ち受けます。

Mac・Linux の場合は、`python3 -m pip install -r requirements.txt` してから `python3 dev.py` を実行してください。

※ ローカル編集は**公開サイトを直接書き換えません**。公開サイトへ反映するには、保存したMarkdownを GitHub へ push するか、公開サイト側の管理画面から編集してください。

## 公開後、ブラウザだけで記事を編集できるようにする

この設定は**最初の一度だけ**必要です。このプロジェクトでは `Ramemaru/lbol-guide` を利用する前提で設定済みですが、**リポジトリ作成・Netlify連携・OAuth設定はまだ必要です**。

### 1. GitHub リポジトリに登録（最初の一度だけ）

- GitHubの **Ramemaru** アカウントで、**新しい**リポジトリを `lbol-guide` の名前で作り、このプロジェクトのソースを登録します。`dist/` は自動生成物なのでリポジトリに登録する必要はありません。ブラウザでアップロードする場合は、このZIPを解凍して、プロジェクト直下のファイルとフォルダをアップロードしてください（ZIP本体だけを入れないでください）。
- `admin/config.yml` は `repo: Ramemaru/lbol-guide` に設定済みです。別の名前で作成する場合に限り、この行を変更してください。
- リポジトリの通常ブランチを `main` とします（異なる場合は `branch:` を変更）。

### 2. Netlify に GitHub リポジトリを連携

- Netlifyで **Add new project → Import a Git repository → GitHub** の順に選びます。
- このリポジトリを選ぶと、同梱の `netlify.toml` がビルド設定を読み込みます。
- 実行コマンド：`python3 -m pip install -r requirements.txt && python3 build.py`
- 公開ディレクトリ：`dist`

**重要**：以前の「Netlify Dropに `dist/` をドラッグする方法」では、CMSからの更新を自動公開できません。**GitHubと連携したデプロイが必要**です。

### 3. GitHubログインを有効化

NetlifyのGit Gatewayは現在非推奨なので、**GitHubバックエンド＋NetlifyのOAuthプロバイダ**を使います。

1. GitHubで [Settings → Developer settings → OAuth Apps](https://github.com/settings/developers) を開き、「New OAuth App」を作成します。
2. Application name は任意。Homepage URL はNetlifyの公開サイトURL、**Authorization callback URL は `https://api.netlify.com/auth/done`** とします。
3. GitHubが発行した **Client ID** と **Client Secret** を、Netlifyの対象サイトの **Project configuration → Security → OAuth → Authentication providers → Install provider → GitHub** に入力します。
4. 公開サイトの `https://＜あなたのサイト名＞.netlify.app/admin/` へアクセスし、GitHubでログインします。

Client Secretは**Netlifyの設定画面にだけ入力**します。ソースコード、GitHub、ChatGPTには貼らないでください。
記事を編集できるのは、対象リポジトリへの書き込み権限を持つGitHubユーザーのみです。

### 4. 投稿から公開まで

1. `/admin/` で「カード解説」などを選択 →「新規作成」。
2. タイトル、URL用ID、文章、必要なら画像を入力。
3. まず「下書きON」で保存し、内容がまとまったら「下書きOFF」にして再保存。
4. 数分後、Netlifyのビルドが成功すると公開記事に反映されます。ビルドの成否はNetlifyの管理画面で確認してください。

公開操作ボタンのラベルは管理画面のバージョン・日本語訳によって変わる場合があります。ここでいう「保存」は、GitHubに変更をコミットする操作を指します。

## 入力の注意

- **URL用ID（slug）**は英小文字、数字、ハイフンのみ。例：`laser-cannon`。これが記事URL `/cards/laser-cannon/` になります。
- 記事を最初に保存したあとは、URL用IDを変更しないでください。ファイル名は自動では変更されないため、URLと一致しなくなります。
- 最終確認日や対象バージョンは空欄でも構いません。推測したゲーム情報は書きません。
- 見本記事を本当の記事に直すときは、タイトルや本文を適切に変更し、**「見本記事」をOFF**にしてください。
- 画像は `assets/uploads/` に保存され、Markdown本文の `/assets/uploads/...` 参照はローカル閲覧向けにも自動変換されます。
- 解説の文章に他の記事をリンクする場合は `[カード解説](/cards/記事のID/)` のように書けます。

## 構成

```text
lbol-guide-cms/
├─ admin/
│  ├─ index.html       # Decap CMSの編集画面
│  └─ config.yml       # 入力項目・GitHub連携の設定
├─ content/
│  ├─ cards/           # カード解説
│  ├─ bosses/          # ボス攻略
│  └─ characters/      # キャラ別攻略
├─ assets/uploads/     # 画像の保存先
├─ templates/          # 公開サイトのHTML
├─ build.py            # Markdown → HTML の生成
├─ dev.py              # ローカル編集 + 自動再生成
├─ start-editor.bat     # Windows向け一括起動
├─ netlify.toml         # GitHub連携後の自動公開設定
└─ dist/               # 生成済みサイト。手動編集しない
```

## トラブルシューティング

- **公開サイトの管理画面にログインできない**：`admin/config.yml` の `repo` とNetlify OAuthの設定を確認してください。
- **ローカルでGitHubログイン画面が表示される**：`npx decap-server` が起動できていない可能性があります。Node.js 20以上か確認してください。
- **保存した記事が公開されない**：`下書き` がONのままでないか、Netlifyのビルドが成功しているか確認してください。
- **記事に画像が表示されない**：画像が `assets/uploads/` に保存されているか、公開ビルド後のURLが `/assets/uploads/画像名` かを確認してください。

## 公開するときの注意

このサイトは非公式の個人攻略サイトを想定しています。ゲーム内画像の掲載には権利者の利用条件を確認してください。GitHubリポジトリを公開設定にした場合、**下書きのMarkdown本文もGitHub上では閲覧できる**ので、非公開にしたい内容は別途管理してください。GitHubリポジトリを非公開にする場合は、Netlifyの料金・デプロイ権限設定をご確認ください。

### 参考資料

- [Decap CMS: GitHub backend](https://decapcms.org/docs/github-backend/)
- [Decap CMS: Local backend](https://decapcms.org/docs/decap-proxy/)
- [Netlify: OAuth provider setup](https://docs.netlify.com/manage/security/secure-access-to-sites/oauth-provider-tokens/)
- [Netlify: Git Gateway (deprecated)](https://docs.netlify.com/manage/security/secure-access-to-sites/git-gateway/)
