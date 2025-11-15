"""
Microsoft Teams integration service using MS Graph API.
"""
import os
from typing import Optional, Dict, Any
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.chat_message import ChatMessage
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType

from app.models.contract import Contract
from app.models.user import User


class TeamsService:
    """Service for sending notifications to Microsoft Teams."""

    def __init__(self):
        """Initialize Teams service with Azure AD configuration."""
        self.tenant_id = os.getenv("AZURE_TENANT_ID", "")
        self.client_id = os.getenv("AZURE_CLIENT_ID", "")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET", "")
        self.team_id = os.getenv("TEAMS_TEAM_ID", "")
        self.channel_id = os.getenv("TEAMS_CHANNEL_ID", "")

        self.enabled = bool(
            self.tenant_id and
            self.client_id and
            self.client_secret and
            self.team_id and
            self.channel_id
        )

        if self.enabled:
            try:
                # Create credential using client secret
                credential = ClientSecretCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )

                # Initialize Graph client
                self.graph_client = GraphServiceClient(credentials=credential)
            except Exception as e:
                print(f"Failed to initialize Teams service: {str(e)}")
                self.enabled = False

    async def send_message(
        self,
        message: str,
        content_type: str = "html",
    ) -> bool:
        """
        Send a message to the configured Teams channel.

        Args:
            message: Message content (HTML or plain text)
            content_type: Content type ('html' or 'text')

        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.enabled:
            print("Teams integration not enabled. Skipping notification.")
            return False

        try:
            # Create chat message
            chat_message = ChatMessage()
            chat_message.body = ItemBody()
            chat_message.body.content = message
            chat_message.body.content_type = (
                BodyType.Html if content_type == "html" else BodyType.Text
            )

            # Send message to channel
            await self.graph_client.teams.by_team_id(
                self.team_id
            ).channels.by_channel_id(
                self.channel_id
            ).messages.post(chat_message)

            return True

        except Exception as e:
            print(f"Failed to send Teams message: {str(e)}")
            return False

    async def send_contract_created_notification(
        self,
        contract: Contract,
        creator: User,
    ) -> bool:
        """
        Send notification when a new contract is created.

        Args:
            contract: Created contract
            creator: User who created the contract

        Returns:
            True if notification sent successfully
        """
        message = f"""
        <h3>🆕 New Contract Created</h3>
        <ul>
            <li><strong>Title:</strong> {contract.title}</li>
            <li><strong>ID:</strong> #{contract.id}</li>
            <li><strong>Counterparty:</strong> {contract.counterparty_name}</li>
            <li><strong>Status:</strong> {contract.status}</li>
            <li><strong>Created by:</strong> {creator.full_name}</li>
        </ul>
        """
        return await self.send_message(message)

    async def send_contract_status_changed_notification(
        self,
        contract: Contract,
        old_status: str,
        new_status: str,
        changed_by: User,
    ) -> bool:
        """
        Send notification when contract status changes.

        Args:
            contract: Contract with updated status
            old_status: Previous status
            new_status: New status
            changed_by: User who changed the status

        Returns:
            True if notification sent successfully
        """
        # Use different emojis based on status
        status_emoji = {
            "draft": "📝",
            "pending_review": "👀",
            "approved": "✅",
            "rejected": "❌",
            "active": "🟢",
            "completed": "✔️",
            "cancelled": "🚫",
        }

        emoji = status_emoji.get(new_status.lower(), "📋")

        message = f"""
        <h3>{emoji} Contract Status Changed</h3>
        <ul>
            <li><strong>Title:</strong> {contract.title}</li>
            <li><strong>ID:</strong> #{contract.id}</li>
            <li><strong>Previous Status:</strong> {old_status}</li>
            <li><strong>New Status:</strong> {new_status}</li>
            <li><strong>Changed by:</strong> {changed_by.full_name}</li>
        </ul>
        """
        return await self.send_message(message)

    async def send_contract_assigned_notification(
        self,
        contract: Contract,
        assigned_to: User,
        assigned_by: User,
    ) -> bool:
        """
        Send notification when a contract is assigned.

        Args:
            contract: Contract that was assigned
            assigned_to: User who was assigned the contract
            assigned_by: User who made the assignment

        Returns:
            True if notification sent successfully
        """
        message = f"""
        <h3>👤 Contract Assigned</h3>
        <ul>
            <li><strong>Title:</strong> {contract.title}</li>
            <li><strong>ID:</strong> #{contract.id}</li>
            <li><strong>Assigned to:</strong> {assigned_to.full_name}</li>
            <li><strong>Assigned by:</strong> {assigned_by.full_name}</li>
        </ul>
        """
        return await self.send_message(message)

    async def send_contract_reminder_notification(
        self,
        contract: Contract,
        reminder_type: str = "expiring",
    ) -> bool:
        """
        Send reminder notification for contract.

        Args:
            contract: Contract to remind about
            reminder_type: Type of reminder

        Returns:
            True if notification sent successfully
        """
        end_date_str = contract.end_date.strftime("%Y-%m-%d") if contract.end_date else "Not set"

        message = f"""
        <h3>⏰ Contract Reminder</h3>
        <ul>
            <li><strong>Title:</strong> {contract.title}</li>
            <li><strong>ID:</strong> #{contract.id}</li>
            <li><strong>End Date:</strong> {end_date_str}</li>
            <li><strong>Reminder Type:</strong> {reminder_type}</li>
        </ul>
        """
        return await self.send_message(message)

    async def send_custom_notification(
        self,
        title: str,
        details: Dict[str, Any],
        emoji: str = "📢",
    ) -> bool:
        """
        Send a custom notification to Teams.

        Args:
            title: Notification title
            details: Dictionary of key-value pairs to display
            emoji: Emoji to use in the title

        Returns:
            True if notification sent successfully
        """
        details_html = "\n".join([
            f"<li><strong>{key}:</strong> {value}</li>"
            for key, value in details.items()
        ])

        message = f"""
        <h3>{emoji} {title}</h3>
        <ul>
            {details_html}
        </ul>
        """
        return await self.send_message(message)


# Global Teams service instance
teams_service = TeamsService()
