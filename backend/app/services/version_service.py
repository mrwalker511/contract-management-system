"""
Version tracking service for contract history.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.contract import Contract
from app.models.contract_version import ContractVersion
from app.models.user import User


class VersionService:
    """Service for managing contract version history."""

    @staticmethod
    def create_version(
        db: Session,
        contract: Contract,
        user: User,
        change_summary: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
    ) -> ContractVersion:
        """
        Create a new version snapshot of a contract.

        Args:
            db: Database session
            contract: Contract to version
            user: User who made the changes
            change_summary: Human-readable summary of changes
            changes: Dictionary of field changes (before/after)

        Returns:
            Created ContractVersion instance
        """
        # Get the current version number
        latest_version = (
            db.query(ContractVersion)
            .filter(ContractVersion.contract_id == contract.id)
            .order_by(ContractVersion.version_number.desc())
            .first()
        )

        version_number = 1 if latest_version is None else latest_version.version_number + 1

        # Create version snapshot with current contract data
        version = ContractVersion(
            contract_id=contract.id,
            version_number=version_number,
            title=contract.title,
            description=contract.description,
            content=contract.content,
            status=contract.status,
            contract_value=contract.contract_value,
            currency=contract.currency,
            counterparty_name=contract.counterparty_name,
            counterparty_contact=contract.counterparty_contact,
            start_date=contract.start_date,
            end_date=contract.end_date,
            changed_by_id=user.id,
            change_summary=change_summary,
            changes_json=changes,
        )

        db.add(version)
        db.commit()
        db.refresh(version)

        return version

    @staticmethod
    def get_contract_versions(
        db: Session,
        contract_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ContractVersion]:
        """
        Get all versions of a contract.

        Args:
            db: Database session
            contract_id: Contract ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ContractVersion instances ordered by version number descending
        """
        return (
            db.query(ContractVersion)
            .filter(ContractVersion.contract_id == contract_id)
            .order_by(ContractVersion.version_number.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_version_by_number(
        db: Session,
        contract_id: int,
        version_number: int,
    ) -> Optional[ContractVersion]:
        """
        Get a specific version of a contract.

        Args:
            db: Database session
            contract_id: Contract ID
            version_number: Version number to retrieve

        Returns:
            ContractVersion instance or None if not found
        """
        return (
            db.query(ContractVersion)
            .filter(
                ContractVersion.contract_id == contract_id,
                ContractVersion.version_number == version_number,
            )
            .first()
        )

    @staticmethod
    def get_latest_version(
        db: Session,
        contract_id: int,
    ) -> Optional[ContractVersion]:
        """
        Get the latest version of a contract.

        Args:
            db: Database session
            contract_id: Contract ID

        Returns:
            Latest ContractVersion instance or None if no versions exist
        """
        return (
            db.query(ContractVersion)
            .filter(ContractVersion.contract_id == contract_id)
            .order_by(ContractVersion.version_number.desc())
            .first()
        )

    @staticmethod
    def compare_versions(
        db: Session,
        contract_id: int,
        version_1: int,
        version_2: int,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare two versions of a contract and return the differences.

        Args:
            db: Database session
            contract_id: Contract ID
            version_1: First version number
            version_2: Second version number

        Returns:
            Dictionary of differences with format:
            {field: {"version_1": value, "version_2": value}}
        """
        v1 = VersionService.get_version_by_number(db, contract_id, version_1)
        v2 = VersionService.get_version_by_number(db, contract_id, version_2)

        if not v1 or not v2:
            return {}

        # Fields to compare
        compare_fields = [
            "title",
            "description",
            "content",
            "status",
            "contract_value",
            "currency",
            "counterparty_name",
            "counterparty_contact",
            "start_date",
            "end_date",
        ]

        differences = {}
        for field in compare_fields:
            val1 = getattr(v1, field)
            val2 = getattr(v2, field)

            if val1 != val2:
                # Convert dates to ISO strings for JSON
                if isinstance(val1, datetime):
                    val1 = val1.isoformat()
                if isinstance(val2, datetime):
                    val2 = val2.isoformat()

                differences[field] = {
                    f"version_{version_1}": val1,
                    f"version_{version_2}": val2,
                }

        return differences

    @staticmethod
    def restore_version(
        db: Session,
        contract: Contract,
        version_number: int,
        user: User,
    ) -> Optional[Contract]:
        """
        Restore a contract to a previous version.

        Args:
            db: Database session
            contract: Contract to restore
            version_number: Version number to restore to
            user: User performing the restore

        Returns:
            Updated Contract instance or None if version not found
        """
        version = VersionService.get_version_by_number(db, contract.id, version_number)

        if not version:
            return None

        # Save current state as a new version before restoring
        VersionService.create_version(
            db=db,
            contract=contract,
            user=user,
            change_summary=f"Before restoring to version {version_number}",
        )

        # Restore fields from the version
        contract.title = version.title
        contract.description = version.description
        contract.content = version.content
        contract.status = version.status
        contract.contract_value = version.contract_value
        contract.currency = version.currency
        contract.counterparty_name = version.counterparty_name
        contract.counterparty_contact = version.counterparty_contact
        contract.start_date = version.start_date
        contract.end_date = version.end_date
        contract.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(contract)

        # Create a new version entry for the restore
        VersionService.create_version(
            db=db,
            contract=contract,
            user=user,
            change_summary=f"Restored to version {version_number}",
        )

        return contract

    @staticmethod
    def delete_contract_versions(
        db: Session,
        contract_id: int,
    ) -> int:
        """
        Delete all versions of a contract.
        Usually called when a contract is permanently deleted.

        Args:
            db: Database session
            contract_id: Contract ID

        Returns:
            Number of versions deleted
        """
        count = (
            db.query(ContractVersion)
            .filter(ContractVersion.contract_id == contract_id)
            .delete()
        )
        db.commit()
        return count
