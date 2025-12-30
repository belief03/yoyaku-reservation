"""
メール送信サービス
予約確認、リマインダーなどのメール送信を管理
"""
from typing import Optional, List
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from api.utils import format_datetime_jp, format_currency
from api.logger import logger


class EmailService:
    """メール送信サービスクラス"""
    
    def __init__(self):
        """初期化"""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM or settings.SMTP_USER
        
        # SSL/TLS設定の自動判定
        # ポート465の場合はSSL、587の場合はSTARTTLS（デフォルト）
        # 明示的に設定されている場合はそれを使用
        if settings.SMTP_USE_SSL:
            self.use_ssl = True
            self.use_tls = False
        elif settings.SMTP_USE_TLS:
            self.use_ssl = False
            self.use_tls = True
        else:
            # ポート番号から自動判定
            if self.smtp_port == 465:
                self.use_ssl = True
                self.use_tls = False
            elif self.smtp_port == 587:
                self.use_ssl = False
                self.use_tls = True
            else:
                # デフォルトはSTARTTLS
                self.use_ssl = False
                self.use_tls = True
        
        self.enabled = bool(self.smtp_host and self.smtp_user and self.smtp_password)
        
        if self.enabled:
            connection_type = "SSL" if self.use_ssl else ("STARTTLS" if self.use_tls else "なし")
            logger.info(f"メール送信サービスが有効です。SMTP: {self.smtp_host}:{self.smtp_port} ({connection_type}), FROM: {self.email_from}")
        else:
            missing = []
            if not self.smtp_host:
                missing.append("SMTP_HOST")
            if not self.smtp_user:
                missing.append("SMTP_USER")
            if not self.smtp_password:
                missing.append("SMTP_PASSWORD")
            logger.warning(f"メール送信サービスが無効です。以下の環境変数が設定されていません: {', '.join(missing)}")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> bool:
        """
        メールを送信
        
        Args:
            to_email: 送信先メールアドレス
            subject: 件名
            body_html: HTML本文
            body_text: テキスト本文（オプション）
        
        Returns:
            送信成功の場合True
        """
        if not self.enabled:
            missing = []
            if not self.smtp_host:
                missing.append("SMTP_HOST")
            if not self.smtp_user:
                missing.append("SMTP_USER")
            if not self.smtp_password:
                missing.append("SMTP_PASSWORD")
            logger.error(
                f"メール送信が無効です。SMTP設定が不足しています。送信先: {to_email}, 件名: {subject}\n"
                f"不足している設定: {', '.join(missing) if missing else 'なし'}\n"
                f"現在の設定 - HOST: {self.smtp_host or '未設定'}, PORT: {self.smtp_port}, "
                f"USER: {self.smtp_user or '未設定'}, FROM: {self.email_from or '未設定'}"
            )
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = to_email
            
            if body_text:
                part1 = MIMEText(body_text, 'plain', 'utf-8')
                msg.attach(part1)
            
            part2 = MIMEText(body_html, 'html', 'utf-8')
            msg.attach(part2)
            
            connection_type = "SSL" if self.use_ssl else ("STARTTLS" if self.use_tls else "なし")
            logger.info(f"メール送信を試行します。送信先: {to_email}, 件名: {subject}, SMTP: {self.smtp_host}:{self.smtp_port} ({connection_type})")
            
            # SSL接続（ポート465など）
            if self.use_ssl:
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            # STARTTLS接続（ポート587など）
            elif self.use_tls:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            # 暗号化なし（非推奨、テスト用のみ）
            else:
                logger.warning("暗号化なしでメール送信を試行します（非推奨）")
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            
            logger.info(f"メール送信成功。送信先: {to_email}, 件名: {subject}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(
                f"SMTP認証エラー: {str(e)}\n"
                f"送信先: {to_email}, 件名: {subject}\n"
                f"SMTP設定 - HOST: {self.smtp_host}, PORT: {self.smtp_port}, USER: {self.smtp_user}\n"
                f"ユーザー名またはパスワードが正しくない可能性があります。"
            )
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(
                f"SMTP接続エラー: {str(e)}\n"
                f"送信先: {to_email}, 件名: {subject}\n"
                f"SMTPサーバー({self.smtp_host}:{self.smtp_port})に接続できません。\n"
                f"ファイアウォールやネットワーク設定を確認してください。"
            )
            return False
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(
                f"SMTP受信者拒否エラー: {str(e)}\n"
                f"送信先: {to_email}, 件名: {subject}\n"
                f"メールアドレスが無効または拒否されています。"
            )
            return False
        except smtplib.SMTPSenderRefused as e:
            logger.error(
                f"SMTP送信者拒否エラー: {str(e)}\n"
                f"送信先: {to_email}, 件名: {subject}\n"
                f"送信者アドレス({self.email_from})が拒否されています。"
            )
            return False
        except smtplib.SMTPDataError as e:
            logger.error(
                f"SMTPデータエラー: {str(e)}\n"
                f"送信先: {to_email}, 件名: {subject}\n"
                f"メールデータが拒否されました。"
            )
            return False
        except smtplib.SMTPException as e:
            logger.error(
                f"SMTPエラー: {str(e)}\n"
                f"送信先: {to_email}, 件名: {subject}\n"
                f"SMTP設定 - HOST: {self.smtp_host}, PORT: {self.smtp_port}"
            )
            return False
        except Exception as e:
            logger.error(
                f"メール送信エラー: {type(e).__name__}: {str(e)}\n"
                f"送信先: {to_email}, 件名: {subject}\n"
                f"SMTP設定 - HOST: {self.smtp_host}, PORT: {self.smtp_port}, USER: {self.smtp_user}"
            )
            import traceback
            logger.error(f"エラー詳細: {traceback.format_exc()}")
            return False
    
    def send_reservation_confirmation(
        self,
        customer_email: str,
        customer_name: str,
        reservation_datetime: datetime,
        service_name: str,
        stylist_name: Optional[str] = None,
        reservation_id: Optional[str] = None
    ) -> bool:
        """予約確認メールを送信"""
        subject = "【予約確認】ご予約ありがとうございます"
        
        datetime_str = format_datetime_jp(reservation_datetime)
        stylist_info = f"<p>スタイリスト: {stylist_name}</p>" if stylist_name else ""
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a90e2;">予約確認</h2>
                <p>お客様</p>
                <p>この度はご予約いただき、誠にありがとうございます。</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin-top: 0;">予約詳細</h3>
                    <p><strong>お名前:</strong> {customer_name}</p>
                    <p><strong>日時:</strong> {datetime_str}</p>
                    <p><strong>サービス:</strong> {service_name}</p>
                    {stylist_info}
                </div>
                
                <p>ご予約の変更やキャンセルをご希望の場合は、お早めにご連絡ください。</p>
                <p>お待ちしております。</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">このメールは自動送信されています。</p>
            </div>
        </body>
        </html>
        """
        
        body_text = f"""
予約確認

お客様

この度はご予約いただき、誠にありがとうございます。

予約詳細
お名前: {customer_name}
日時: {datetime_str}
サービス: {service_name}
{('スタイリスト: ' + stylist_name) if stylist_name else ''}

ご予約の変更やキャンセルをご希望の場合は、お早めにご連絡ください。
お待ちしております。
        """
        
        return self.send_email(customer_email, subject, body_html, body_text)
    
    def send_reservation_reminder(
        self,
        customer_email: str,
        customer_name: str,
        reservation_datetime: datetime,
        service_name: str,
        hours_before: int = 24
    ) -> bool:
        """予約リマインダーメールを送信"""
        subject = f"【リマインダー】{hours_before}時間後にご予約がございます"
        
        datetime_str = format_datetime_jp(reservation_datetime)
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a90e2;">予約リマインダー</h2>
                <p>{customer_name}様</p>
                <p>{hours_before}時間後にご予約がございます。</p>
                
                <div style="background-color: #fff3cd; padding: 15px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #ffc107;">
                    <h3 style="margin-top: 0;">予約詳細</h3>
                    <p><strong>日時:</strong> {datetime_str}</p>
                    <p><strong>サービス:</strong> {service_name}</p>
                </div>
                
                <p>お時間に余裕を持ってお越しください。</p>
                <p>ご予約の変更やキャンセルをご希望の場合は、お早めにご連絡ください。</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">このメールは自動送信されています。</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, body_html)
    
    def send_reservation_cancellation(
        self,
        customer_email: str,
        customer_name: str,
        reservation_datetime: datetime,
        service_name: str,
        reason: Optional[str] = None
    ) -> bool:
        """予約キャンセル確認メールを送信"""
        subject = "【予約キャンセル】ご予約のキャンセルを承りました"
        
        datetime_str = format_datetime_jp(reservation_datetime)
        reason_text = f"<p><strong>キャンセル理由:</strong> {reason}</p>" if reason else ""
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #e74c3c;">予約キャンセル確認</h2>
                <p>{customer_name}様</p>
                <p>以下のご予約のキャンセルを承りました。</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin-top: 0;">キャンセルした予約</h3>
                    <p><strong>日時:</strong> {datetime_str}</p>
                    <p><strong>サービス:</strong> {service_name}</p>
                    {reason_text}
                </div>
                
                <p>またのご利用をお待ちしております。</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">このメールは自動送信されています。</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, body_html)
    
    def send_order_confirmation(
        self,
        customer_email: str,
        customer_name: str,
        order_id: str,
        total_amount: int,
        items: List[dict]
    ) -> bool:
        """注文確認メールを送信"""
        subject = "【注文確認】ご注文ありがとうございます"
        
        items_html = ""
        for item in items:
            items_html += f"<li>{item.get('name', '')} × {item.get('quantity', 1)} - {format_currency(item.get('unit_price', 0) * item.get('quantity', 1))}</li>"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a90e2;">注文確認</h2>
                <p>{customer_name}様</p>
                <p>この度はご注文いただき、誠にありがとうございます。</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin-top: 0;">注文詳細</h3>
                    <p><strong>注文ID:</strong> {order_id}</p>
                    <ul>
                        {items_html}
                    </ul>
                    <p style="font-size: 18px; font-weight: bold; margin-top: 15px;">
                        合計金額: {format_currency(total_amount)}
                    </p>
                </div>
                
                <p>ご注文の処理を開始いたします。</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">このメールは自動送信されています。</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, body_html)
    
    def send_invitation_email(
        self,
        to_email: str,
        invitation_url: str,
        shop_name: Optional[str] = None
    ) -> bool:
        """招待メールを送信"""
        subject = "【招待】予約システムへのご招待"
        
        shop_name_text = shop_name if shop_name else "新しい店舗"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a90e2;">予約システムへのご招待</h2>
                <p>こんにちは</p>
                <p>予約システムへのご招待をいたします。以下のリンクから店舗アカウントの設定を行ってください。</p>
                
                <div style="background-color: #e7f3ff; padding: 20px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #4a90e2;">
                    <h3 style="margin-top: 0; color: #4a90e2;">店舗情報</h3>
                    <p><strong>店舗名:</strong> {shop_name_text}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{invitation_url}" 
                       style="display: inline-block; background-color: #4a90e2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        アカウント設定を開始する
                    </a>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #ffc107;">
                    <p style="margin: 0; font-size: 14px;">
                        <strong>ご注意:</strong><br>
                        この招待リンクは7日間有効です。期限が切れる前に設定を完了してください。<br>
                        もしこのメールに心当たりがない場合は、このメールを無視してください。
                    </p>
                </div>
                
                <p style="font-size: 14px; color: #666;">
                    上記のボタンがクリックできない場合は、以下のURLをコピーしてブラウザに貼り付けてください：<br>
                    <a href="{invitation_url}" style="color: #4a90e2; word-break: break-all;">{invitation_url}</a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">このメールは自動送信されています。</p>
            </div>
        </body>
        </html>
        """
        
        body_text = f"""
予約システムへのご招待

こんにちは

予約システムへのご招待をいたします。以下のリンクから店舗アカウントの設定を行ってください。

店舗情報
店舗名: {shop_name_text}

招待リンク:
{invitation_url}

ご注意:
この招待リンクは7日間有効です。期限が切れる前に設定を完了してください。
もしこのメールに心当たりがない場合は、このメールを無視してください。

このメールは自動送信されています。
        """
        
        return self.send_email(to_email, subject, body_html, body_text)


def get_email_service() -> EmailService:
    """メールサービスのインスタンスを取得"""
    return EmailService()





