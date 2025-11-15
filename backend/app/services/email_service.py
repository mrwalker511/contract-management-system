"""
Email notification service using SMTP.
"""
import os
from typing import List, Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from app.models.user import User
from app.models.contract import Contract


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from_email = os.getenv("SMTP_FROM_EMAIL", "noreply@contractmanagement.com")
        self.smtp_from_name = os.getenv("SMTP_FROM_NAME", "Contract Management System")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

        # Initialize Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        template_dir.mkdir(parents=True, exist_ok=True)

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML body of the email
            text_content: Plain text body (optional, will use HTML if not provided)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.smtp_from_name} <{self.smtp_from_email}>"
            message["To"] = to_email

            # Add plain text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)

            part2 = MIMEText(html_content, "html")
            message.attach(part2)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=self.smtp_use_tls,
            )

            return True

        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_bulk_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> Dict[str, bool]:
        """
        Send the same email to multiple recipients.

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML body of the email
            text_content: Plain text body (optional)

        Returns:
            Dictionary mapping email addresses to success status
        """
        results = {}
        for email in to_emails:
            results[email] = await self.send_email(email, subject, html_content, text_content)
        return results

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render an email template with the given context.

        Args:
            template_name: Name of the template file (e.g., "contract_created.html")
            context: Dictionary of variables to pass to the template

        Returns:
            Rendered HTML string
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            print(f"Failed to render template {template_name}: {str(e)}")
            return ""

    async def send_contract_created_notification(
        self,
        contract: Contract,
        creator: User,
        recipients: List[str],
    ) -> Dict[str, bool]:
        """
        Send notification when a new contract is created.

        Args:
            contract: Created contract
            creator: User who created the contract
            recipients: List of email addresses to notify

        Returns:
            Dictionary mapping email addresses to success status
        """
        context = {
            "contract_title": contract.title,
            "contract_id": contract.id,
            "counterparty": contract.counterparty_name,
            "creator_name": creator.full_name,
            "status": contract.status,
        }

        html_content = self.render_template("contract_created.html", context)
        subject = f"New Contract Created: {contract.title}"

        return await self.send_bulk_email(recipients, subject, html_content)

    async def send_contract_status_changed_notification(
        self,
        contract: Contract,
        old_status: str,
        new_status: str,
        changed_by: User,
        recipients: List[str],
    ) -> Dict[str, bool]:
        """
        Send notification when contract status changes.

        Args:
            contract: Contract with updated status
            old_status: Previous status
            new_status: New status
            changed_by: User who changed the status
            recipients: List of email addresses to notify

        Returns:
            Dictionary mapping email addresses to success status
        """
        context = {
            "contract_title": contract.title,
            "contract_id": contract.id,
            "old_status": old_status,
            "new_status": new_status,
            "changed_by_name": changed_by.full_name,
        }

        html_content = self.render_template("contract_status_changed.html", context)
        subject = f"Contract Status Changed: {contract.title}"

        return await self.send_bulk_email(recipients, subject, html_content)

    async def send_contract_assigned_notification(
        self,
        contract: Contract,
        assigned_to: User,
        assigned_by: User,
    ) -> bool:
        """
        Send notification when a contract is assigned to a user.

        Args:
            contract: Contract that was assigned
            assigned_to: User who was assigned the contract
            assigned_by: User who made the assignment

        Returns:
            True if email sent successfully
        """
        context = {
            "contract_title": contract.title,
            "contract_id": contract.id,
            "assigned_by_name": assigned_by.full_name,
            "assigned_to_name": assigned_to.full_name,
        }

        html_content = self.render_template("contract_assigned.html", context)
        subject = f"Contract Assigned to You: {contract.title}"

        return await self.send_email(assigned_to.email, subject, html_content)

    async def send_contract_reminder_notification(
        self,
        contract: Contract,
        recipients: List[str],
        reminder_type: str = "expiring",
    ) -> Dict[str, bool]:
        """
        Send reminder notification for contract (e.g., expiring soon).

        Args:
            contract: Contract to remind about
            recipients: List of email addresses to notify
            reminder_type: Type of reminder (expiring, review_needed, etc.)

        Returns:
            Dictionary mapping email addresses to success status
        """
        context = {
            "contract_title": contract.title,
            "contract_id": contract.id,
            "end_date": contract.end_date.isoformat() if contract.end_date else "Not set",
            "reminder_type": reminder_type,
        }

        html_content = self.render_template("contract_reminder.html", context)
        subject = f"Contract Reminder: {contract.title}"

        return await self.send_bulk_email(recipients, subject, html_content)

    async def send_welcome_email(self, user: User) -> bool:
        """
        Send welcome email to new user.

        Args:
            user: Newly registered user

        Returns:
            True if email sent successfully
        """
        context = {
            "user_name": user.full_name,
            "user_email": user.email,
            "user_role": user.role,
        }

        html_content = self.render_template("welcome.html", context)
        subject = "Welcome to Contract Management System"

        return await self.send_email(user.email, subject, html_content)


# Global email service instance
email_service = EmailService()
