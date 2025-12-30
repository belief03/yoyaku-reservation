# メール送信設定ガイド

## 📧 メール送信機能の概要

現在の実装では、**SMTPサーバー**を使用したメール送信機能が実装されています。

## 🔧 設定方法

### 方法1: SMTPサーバーを使用（推奨・現在の実装）

最も一般的で柔軟な方法です。Gmail、SendGrid、MailgunなどのSMTPサーバーを使用できます。

#### 環境変数の設定

`.env`ファイルに以下を追加：

```env
# SMTP設定
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

#### Gmailを使用する場合

1. Googleアカウントで「アプリパスワード」を生成
   - Googleアカウント設定 → セキュリティ → 2段階認証プロセス → アプリパスワード
2. 生成されたパスワードを`SMTP_PASSWORD`に設定

#### SendGridを使用する場合

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
EMAIL_FROM=noreply@yourdomain.com
```

#### Mailgunを使用する場合

```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@yourdomain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
EMAIL_FROM=noreply@yourdomain.com
```

---

### 方法2: Supabaseのメール送信機能を使用

Supabaseにはメール送信機能がありますが、**現在の実装では使用していません**。

Supabaseのメール送信を使用する場合は、以下の変更が必要です：

1. **Supabaseのメール機能を有効化**
   - Supabase Dashboard → Settings → Auth → Email Templates
   - SMTP設定を構成

2. **Supabaseのメール送信APIを使用するようにコードを変更**

```python
# 例: Supabaseのメール送信を使用する場合
from supabase import Client

def send_email_via_supabase(
    db: Client,
    to_email: str,
    subject: str,
    body_html: str
):
    # Supabaseのメール送信機能を使用
    # 注意: Supabaseのメール送信は主に認証メール用
    # カスタムメール送信にはSMTP設定が必要
    pass
```

**注意**: Supabaseの無料プランでは、カスタムメール送信にはSMTP設定が必要です。

---

### 方法3: Vercelのメール送信機能を使用

Vercelには**メール送信機能はありません**。Vercelでメールを送信する場合は、以下のサービスを使用する必要があります：

1. **SendGrid**（推奨）
2. **Mailgun**
3. **Resend**（Vercel推奨）
4. **AWS SES**

#### Resendを使用する場合（Vercel推奨）

```env
# ResendのAPIキーを使用
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=your-resend-api-key
EMAIL_FROM=noreply@yourdomain.com
```

---

## 🚀 デプロイ時の設定

### Vercelにデプロイする場合

1. **Vercel Dashboardで環境変数を設定**
   - Project Settings → Environment Variables
   - 以下の環境変数を追加：
     - `SMTP_HOST`
     - `SMTP_PORT`
     - `SMTP_USER`
     - `SMTP_PASSWORD`
     - `EMAIL_FROM`

2. **推奨サービス**
   - **Resend**: Vercelと統合しやすい
   - **SendGrid**: 無料プランあり、信頼性が高い

### その他のホスティングサービス

- **Heroku**: 環境変数で設定
- **Railway**: 環境変数で設定
- **AWS**: SESを使用可能
- **Google Cloud**: SendGridやGmail SMTPを使用

---

## 📝 現在の実装での動作

### メール送信が無効な場合

環境変数が設定されていない場合、メール送信は**無効**になりますが、エラーにはなりません：

```python
# メール送信が無効な場合のログ
[Email Service] メール送信が無効です。送信先: example@example.com, 件名: 予約確認
```

### メール送信が有効な場合

以下のタイミングでメールが送信されます：

1. **招待メール**: 招待作成時
2. **予約確認メール**: 予約作成時
3. **予約リマインダー**: 予約の24時間前（スクリプト実行時）
4. **予約キャンセルメール**: 予約キャンセル時
5. **注文確認メール**: 注文作成時

---

## ✅ 推奨設定

### 開発環境

```env
# 開発環境ではメール送信を無効にするか、テスト用SMTPサーバーを使用
# SMTP設定をコメントアウトすると、メール送信は無効になります
```

### 本番環境

```env
# SendGrid（推奨）
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@yourdomain.com

# または Resend（Vercel推奨）
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=re_xxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@yourdomain.com
```

---

## 🔍 トラブルシューティング

### メールが送信されない

1. **環境変数が正しく設定されているか確認**
   ```bash
   echo $SMTP_HOST
   echo $SMTP_USER
   ```

2. **SMTPサーバーに接続できるか確認**
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'your-password')
   ```

3. **ログを確認**
   - サーバーのログにエラーメッセージが表示されます

### メールがスパムフォルダに入る

- **SPFレコード**を設定
- **DKIM署名**を設定
- **送信元ドメイン**を認証

---

## 📚 参考リンク

- [SendGrid公式ドキュメント](https://docs.sendgrid.com/)
- [Resend公式ドキュメント](https://resend.com/docs)
- [Mailgun公式ドキュメント](https://documentation.mailgun.com/)
- [Gmail SMTP設定](https://support.google.com/a/answer/176600)


