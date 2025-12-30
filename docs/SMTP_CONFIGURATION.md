# SMTP設定ガイド - 多様なメールサービス対応

## 📧 対応メールサービス

このシステムは以下のメールサービスに対応しています：

- **Gmail** (推奨)
- **SendGrid** (本番環境推奨)
- **Mailgun**
- **Resend** (Vercel推奨)
- **Outlook/Hotmail**
- **Yahoo Mail**
- **AWS SES**
- **その他のカスタムSMTPサーバー**

## 🔧 設定方法

### 基本設定

`.env`ファイルに以下の環境変数を設定します：

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-username
SMTP_PASSWORD=your-password
EMAIL_FROM=noreply@yourdomain.com
```

### SSL/TLS設定（オプション）

ポート番号から自動判定されますが、明示的に指定することも可能です：

```env
# SSL接続を使用する場合（ポート465など）
SMTP_USE_SSL=true

# STARTTLS接続を使用する場合（ポート587など、デフォルト）
SMTP_USE_TLS=true
```

## 📋 メールサービス別の設定例

### 1. Gmail（推奨: ポート587 + STARTTLS）

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

**Gmailアプリパスワードの取得方法**:
1. Googleアカウント設定 → セキュリティ
2. 2段階認証プロセスを有効化
3. アプリパスワードを生成
4. 生成されたパスワードを`SMTP_PASSWORD`に設定

### 2. Gmail（SSL接続: ポート465）

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USE_SSL=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

### 3. SendGrid（本番環境推奨）

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@yourdomain.com
```

**SendGrid APIキーの取得方法**:
1. SendGridアカウントにログイン
2. Settings → API Keys
3. Create API Key
4. 生成されたAPIキーを`SMTP_PASSWORD`に設定
5. `SMTP_USER`は常に`apikey`を使用

### 4. Mailgun

```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@yourdomain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
EMAIL_FROM=noreply@yourdomain.com
```

### 5. Resend（Vercel推奨）

```env
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=re_xxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@yourdomain.com
```

### 6. Outlook/Hotmail

```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
EMAIL_FROM=your-email@outlook.com
```

### 7. Yahoo Mail

```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USER=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@yahoo.com
```

**Yahooアプリパスワードの取得方法**:
1. Yahooアカウント設定 → セキュリティ
2. アプリパスワードを生成
3. 生成されたパスワードを`SMTP_PASSWORD`に設定

### 8. AWS SES

```env
SMTP_HOST=email-smtp.region.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
EMAIL_FROM=noreply@yourdomain.com
```

**AWS SES設定方法**:
1. AWS SESでSMTP認証情報を作成
2. リージョンに応じて`SMTP_HOST`を設定（例: `email-smtp.us-east-1.amazonaws.com`）
3. SMTPユーザー名とパスワードを設定

### 9. その他のカスタムSMTPサーバー

```env
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587
SMTP_USER=your-username
SMTP_PASSWORD=your-password
EMAIL_FROM=noreply@yourdomain.com
# SSL接続の場合は true
SMTP_USE_SSL=false
# STARTTLS接続の場合は true（デフォルト）
SMTP_USE_TLS=true
```

## 🔄 自動判定機能

システムは以下のルールでSSL/TLS接続を自動判定します：

- **ポート465**: SSL接続（`SMTP_SSL`）を使用
- **ポート587**: STARTTLS接続（`SMTP_STARTTLS`）を使用
- **その他のポート**: STARTTLS接続を使用（デフォルト）

明示的に`SMTP_USE_SSL`または`SMTP_USE_TLS`を設定することで、自動判定を上書きできます。

## ✅ 設定確認

設定後、アプリケーションを起動すると、ログに以下のようなメッセージが表示されます：

```
メール送信サービスが有効です。SMTP: smtp.gmail.com:587 (STARTTLS), FROM: your-email@gmail.com
```

## 🚨 トラブルシューティング

### メールが送信されない場合

1. **環境変数が正しく設定されているか確認**
   ```bash
   echo $SMTP_HOST
   echo $SMTP_USER
   ```

2. **ポート番号とSSL/TLS設定を確認**
   - ポート465の場合は`SMTP_USE_SSL=true`
   - ポート587の場合は`SMTP_USE_TLS=true`（デフォルト）

3. **ログを確認**
   - サーバーのログにエラーメッセージが表示されます
   - 認証エラー、接続エラーなどの詳細が記録されます

### よくあるエラー

- **SMTP認証エラー**: ユーザー名またはパスワードが正しくない
- **SMTP接続エラー**: SMTPサーバーに接続できない（ファイアウォール、ネットワーク設定を確認）
- **SSL/TLSエラー**: ポート番号とSSL/TLS設定が一致していない

## 📚 参考リンク

- [SendGrid公式ドキュメント](https://docs.sendgrid.com/)
- [Resend公式ドキュメント](https://resend.com/docs)
- [Mailgun公式ドキュメント](https://documentation.mailgun.com/)
- [AWS SES公式ドキュメント](https://docs.aws.amazon.com/ses/)
- [Gmail SMTP設定](https://support.google.com/mail/answer/7126229)


