# LBoL攻略ノート — 最初の公開設定（1回だけ）

**最終目標**：`https://＜Netlifyのサイト名＞.netlify.app/admin/` を開いて記事を保存すると、公開サイトに自動反映されること。

このパッケージは **GitHub: `Ramemaru/lbol-guide` ／ Netlify: 新規サイト**を想定して `admin/config.yml` を設定済みです。公開・ログインの設定はまだ行われていません。

## GitHub にソースを登録

1. https://github.com/new でリポジトリ名を `lbol-guide` にして作成。オーナーは `Ramemaru` を選びます。公開サイトは友人に見せられますが、リポジトリを **Public** にすると `draft: true` の下書き文章も GitHub 上で誰でも閲覧できます。個人的な下書きを隠したいなら **Private** を選んでください。
2. 新しいリポジトリのページで **Add file → Upload files** を選び、解凍済みのパッケージの *中身*（`admin/`, `assets/`, `content/`, `templates/`, `build.py`, `netlify.toml`, `requirements.txt` など）をドラッグしてアップロードします。**ZIPファイルそのものはアップロードしないでください。** `dist/`, `__pycache__/`, `node_modules/` は不要です。**GitHub のトップレベルに `build.py` と `netlify.toml` がある状態**が正解です。
3. コミットまで完了したら `https://github.com/Ramemaru/lbol-guide` でソースが見えることを確認します。

> GitHub の Web アップロード画面でうまくフォルダをアップロードできなければ、GitHub Desktopでこのフォルダをリポジトリにコミットして公開しても構いません。

## Netlify の Git 自動デプロイを設定

1. https://app.netlify.com/start から **Import an existing project / Import a Git repository** を選び、GitHub を選択。`Ramemaru/lbol-guide` を連携します。
2. ビルドコマンドが空欄の場合は `python3 -m pip install -r requirements.txt && python3 build.py` 、公開ディレクトリは `dist` にします。`netlify.toml` を読み込める場合、これらは既に指定されています。
3. デプロイ後に表示された `https://＜サイト名＞.netlify.app/` を開き、サイトが表示されることを確認します。`/admin/` はこの時点ではまだログインできません。

## Decap CMS から GitHub にログインできるようにする

1. https://github.com/settings/developers → **OAuth Apps → New OAuth App**。
2. アプリ名は `LBoL Guide CMS` など。**Homepage URL** は公開されたNetlifyのURL、**Authorization callback URL** は `https://api.netlify.com/auth/done` を設定します。
3. 作成された **Client ID** と新しく発行した **Client Secret** を控えます。
4. Netlifyで当該サイトを開き、 **Project configuration → Security （または Access & security）→ OAuth → Authentication providers → Install provider → GitHub** からIDとSecretを登録。
5. `https://＜サイト名＞.netlify.app/admin/` を開き、GitHubでログイン。書き込み権限のあるアカウントで記事を保存して、NetlifyのDeploysで更新を確認します。

**Client Secret をGitHubのファイル、ChatGPTへのメッセージ、スクリーンショットに貼らないでください。** Netlifyの設定画面にだけ入力します。

### 動作確認のおすすめ

`/admin/` から新しいカード記事を1件作成し、`下書き`を **ON** のまま保存 → GitHubにコミットができることを確認。その後 `下書き`を **OFF** にして保存 → Netlifyが再ビルドし `/cards/記事のID/` で閲覧できることを確認します。

CMSのログイン後も登録済みのユーザーが全員編集できるわけではありません。GitHubリポジトリへの書き込み権限が必要です。

## サイト構成を後で変えるとき

記事は `content/cards/`, `content/bosses/`, `content/characters/` のMarkdownに保存されます。記事の項目を変えたい場合は `admin/config.yml` を修正し、表示は `templates/` と `build.py` を修正します。通常の記事の追加や編集ではプログラムを触る必要はありません。

Netlify OAuth設定公式ガイド： https://docs.netlify.com/manage/security/secure-access-to-sites/oauth-provider-tokens/  
Decap GitHub backend公式ガイド： https://decapcms.org/docs/github-backend/ 
