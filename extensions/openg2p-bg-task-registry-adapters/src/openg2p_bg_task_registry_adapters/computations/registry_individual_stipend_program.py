from datetime import date, datetime
from typing import Any, Dict, List, Tuple

import numpy as np
from openg2p_bg_task_models.models import BeneficiaryListDetails
from openg2p_bg_task_models.schemas import BeneficiarySearchResponsePayload, RegistrantDetails
from sqlalchemy import TextClause, text, update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from ..interface import RegistryInterface
from ..models import (
    BeneficiaryListSummaryIndividualStipendProgram as SummaryModel,
)
from ..models import G2PIndividualStipendProgramRegistry
from ..models.enums import StipendProgramEnum, WorkTypeEnum
from ..schema import (
    BeneficiaryListSummary,
    BeneficiaryListSummaryIndividualStipendProgram,
    BeneficiaryListSummaryIndividualStipendProgramPayload,
    G2PIndividualStipendProgramRegistryPayload,
)

TARGET = "individual_stipend_program"
VIEW = "g2p_individual_stipend_program_registry"

_PAYLOAD_COLUMNS = (
    "internal_record_id",
    "stipend_program_name",
    "work_type",
    "hours_contributed",
    "contribution_from_date",
    "contribution_to_date",
    "contribution_date_range",
    "record_status",
)


def _row_to_payload(row) -> dict:
    payload = {}
    for col in _PAYLOAD_COLUMNS:
        if col not in row:
            continue
        val = row[col]
        if isinstance(val, datetime):
            payload[col] = val.isoformat()
        elif isinstance(val, date):
            payload[col] = val.isoformat()
        else:
            payload[col] = val
    return payload


def _s(v):
    return str(v) if v is not None else None


class RegistryIndividualStipendProgram(RegistryInterface):
    """Eligibility adapter over g2p_individual_stipend_program_registry."""

    async def get_summary(self, beneficiary_list_id, bg_task_session, formated=False):
        row = (
            await bg_task_session.execute(
                select(SummaryModel).where(
                    SummaryModel.beneficiary_list_id == beneficiary_list_id
                )
            )
        ).scalars().first()
        if not row:
            return None
        return self._summary_payload(row)

    def get_summary_sync(self, beneficiary_list_id, bg_task_session):
        row = (
            bg_task_session.query(SummaryModel)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .first()
        )
        if not row:
            return None
        return self._summary_payload(row)

    def _summary_payload(self, row):
        return BeneficiaryListSummaryIndividualStipendProgramPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=row.id,
                program_id=row.program_id,
                program_mnemonic=row.program_mnemonic,
                target_registry=row.target_registry,
                beneficiary_list_id=row.beneficiary_list_id,
                number_of_registrants=row.number_of_registrants,
                date_created=row.date_created,
                total_disbursement_quantity=getattr(
                    row, "total_disbursement_quantity", None
                ),
                average_entitlement_per_registrant=getattr(
                    row, "average_entitlement_per_person",
                    getattr(row, "average_entitlement_per_registrant", None),
                ),
            ),
            registry_summary=BeneficiaryListSummaryIndividualStipendProgram(
                hours_contributed_mean=_s(getattr(row, "hours_contributed_mean", None)),
                part_time_count=_s(getattr(row, "part_time_count", None)),
                full_time_count=_s(getattr(row, "full_time_count", None)),
                social_protection_count=_s(
                    getattr(row, "social_protection_count", None)
                ),
            ),
        )

    async def search_beneficiaries(
        self,
        bg_task_session,
        sr_session,
        beneficiary_list_id,
        target_registry,
        search_query,
        page=1,
        page_size=10,
        order_by="id asc",
    ) -> Tuple[BeneficiarySearchResponsePayload, int]:
        registrant_ids = await self._registrant_ids(bg_task_session, beneficiary_list_id)
        query, params = self.construct_beneficiary_search_sql_query(
            registrant_ids, target_registry, search_query, order_by, page_size, page
        )
        if query is None:
            return (
                BeneficiarySearchResponsePayload(
                    beneficiary_count=0,
                    beneficiaries=[],
                ),
                0,
            )
        rows = (await sr_session.execute(query, params)).mappings().all()
        count_query, count_params = self.construct_beneficiary_search_count_sql_query(
            registrant_ids, target_registry, search_query
        )
        total = (await sr_session.execute(count_query, count_params)).scalar_one()
        beneficiaries = [
            G2PIndividualStipendProgramRegistryPayload(**_row_to_payload(r))
            for r in rows
        ]
        return (
            BeneficiarySearchResponsePayload(
                beneficiary_count=len(beneficiaries),
                beneficiaries=beneficiaries,
            ),
            total,
        )

    async def _registrant_ids(self, bg_task_session, beneficiary_list_id) -> List[str]:
        rows = (
            await bg_task_session.execute(
                select(BeneficiaryListDetails.registrant_details).where(
                    BeneficiaryListDetails.beneficiary_list_id == beneficiary_list_id
                )
            )
        ).scalars().all()
        ids = []
        for detail in rows:
            for registrant in detail:
                ids.append(registrant["registrant_id"])
        return ids

    def compute_eligibility_statistics(
        self, beneficiary_list_details, base_summary, sr_session, bg_task_session
    ):
        summary = SummaryModel(
            program_id=base_summary.program_id,
            program_mnemonic=base_summary.program_mnemonic,
            target_registry=base_summary.target_registry,
            beneficiary_list_id=base_summary.beneficiary_list_id,
            number_of_registrants=base_summary.number_of_registrants,
            date_created=base_summary.date_created,
        )
        hours: List[int] = []
        part_time = full_time = social_protection = 0
        for detail in beneficiary_list_details:
            registrant_ids = [
                RegistrantDetails(**r).registrant_id for r in detail.registrant_details
            ]
            for row in self.get_registrants_by_ids(registrant_ids, sr_session):
                if row.hours_contributed is not None:
                    hours.append(row.hours_contributed)
                part_time += 1 if row.work_type == WorkTypeEnum.PART_TIME.value else 0
                full_time += 1 if row.work_type == WorkTypeEnum.FULL_TIME.value else 0
                social_protection += (
                    1
                    if row.stipend_program_name
                    == StipendProgramEnum.STIPEND_SOCIAL_SERVICES.value
                    else 0
                )
        if hours:
            summary.hours_contributed_mean = round(sum(hours) / len(hours), 2)
        summary.part_time_count = part_time
        summary.full_time_count = full_time
        summary.social_protection_count = social_protection
        bg_task_session.add(summary)

    def get_registrants_by_ids(
        self, registrant_ids, sr_session
    ) -> List[G2PIndividualStipendProgramRegistry]:
        return list(
            sr_session.query(G2PIndividualStipendProgramRegistry)
            .filter(
                G2PIndividualStipendProgramRegistry.internal_record_id.in_(
                    registrant_ids
                )
            )
            .yield_per(500)
        )

    def construct_beneficiary_search_sql_query(
        self,
        registrant_ids: List[str],
        target_registry: str,
        where_clause: str,
        order_by: str,
        page_size: int,
        page: int,
    ) -> Tuple[TextClause, Dict[str, Any]]:
        if not registrant_ids:
            return None, {}
        where_clause = (where_clause or "").replace("“", '"').replace("”", '"')
        where_clause = where_clause.replace("‘", "'").replace("’", "'")
        where_clause_sql = f" AND {where_clause}" if where_clause else ""
        registrant_placeholders = ", ".join(
            [f":registrant_id_{i}" for i in range(len(registrant_ids))]
        )
        sql_query = text(
            f"""
            SELECT * FROM {VIEW}
            WHERE internal_record_id IN ({registrant_placeholders}) {where_clause_sql}
            ORDER BY {order_by}
            OFFSET :offset
            LIMIT :limit
            """
        )
        params = {
            f"registrant_id_{i}": registrant_ids[i] for i in range(len(registrant_ids))
        }
        params.update({"offset": page_size * (page - 1), "limit": page_size})
        return sql_query, params

    def construct_beneficiary_search_count_sql_query(
        self, registrant_ids: List[str], target_registry: str, where_clause: str
    ) -> Tuple[TextClause, Dict[str, Any]]:
        if not registrant_ids:
            return None, {}
        where_clause = (where_clause or "").replace("“", '"').replace("”", '"')
        where_clause = where_clause.replace("‘", "'").replace("’", "'")
        where_clause_sql = f" AND {where_clause}" if where_clause else ""
        registrant_placeholders = ", ".join(
            [f":registrant_id_{i}" for i in range(len(registrant_ids))]
        )
        sql_query = text(
            f"""
            SELECT COUNT(*) FROM {VIEW}
            WHERE internal_record_id IN ({registrant_placeholders}) {where_clause_sql}
            """
        )
        params = {
            f"registrant_id_{i}": registrant_ids[i] for i in range(len(registrant_ids))
        }
        return sql_query, params

    def construct_multiplier_sql_query(
        self, multiplier: str, target_registry: str
    ) -> TextClause:
        if not multiplier or multiplier == "none":
            return None
        return text(
            f"""
            SELECT {multiplier} FROM {VIEW}
            WHERE internal_record_id = :registrant_id
            """
        )

    def construct_get_is_registrant_entitled_sql_query(
        self, registrant_id: str, target_registry: str, sql_query: str
    ) -> TextClause:
        sql_query = sql_query.strip()
        if not registrant_id:
            raise ValueError("registrant_id cannot be None or zero")
        if not sql_query.upper().startswith("SELECT"):
            raise ValueError("Invalid SQL query: Must be a valid SELECT statement")
        if "WHERE" in sql_query.upper():
            sql_query += f' AND "{VIEW}".internal_record_id = :registrant_id'
        else:
            sql_query += f' WHERE "{VIEW}".internal_record_id = :registrant_id'
        return text(sql_query).params(registrant_id=registrant_id)

    def get_is_registant_entitled(self, registrant_id, sql_query, sr_session) -> bool:
        q = self.construct_get_is_registrant_entitled_sql_query(
            registrant_id, TARGET, sql_query
        )
        return sr_session.execute(q).fetchone() is not None

    def get_entitlement_multiplier(self, multiplier, registrant_id, sr_session) -> int:
        if not multiplier or multiplier == "none":
            return 1
        sql_query = self.construct_multiplier_sql_query(multiplier, TARGET)
        result = sr_session.execute(
            sql_query, {"registrant_id": registrant_id}
        ).fetchone()
        return int(result[0]) if result and result[0] is not None else 1

    def compute_entitlement_statistics(
        self, beneficiary_list_id: str, bg_task_session: Session, sr_session: Session
    ):
        beneficiary_list_details = (
            bg_task_session.query(BeneficiaryListDetails)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .all()
        )

        entitlements: Dict[Any, List[float]] = {}

        for beneficiary_list_detail in beneficiary_list_details:
            for registrant_detail in beneficiary_list_detail.registrant_details:
                registrant_detail = RegistrantDetails(**registrant_detail)
                for benefit_code_id, value in registrant_detail.entitlement.items():
                    entitlements.setdefault(benefit_code_id, []).append(value)

        entitlement_stats = self.compute_stats_dict(entitlements)

        bg_task_session.execute(
            update(SummaryModel)
            .where(SummaryModel.beneficiary_list_id == beneficiary_list_id)
            .values(
                total_disbursement_quantity=dict(entitlement_stats["total"]),
                average_entitlement_per_person=dict(entitlement_stats["average"]),
                entitlement_amount_q1=dict(entitlement_stats["q1"]),
                entitlement_amount_q2=dict(entitlement_stats["q2"]),
                entitlement_amount_q3=dict(entitlement_stats["q3"]),
            )
        )

    def compute_stats_dict(
        self, entitlements_dict: Dict[Any, List[float]]
    ) -> Dict[str, Dict[Any, float]]:
        stats: Dict[str, Dict[Any, float]] = {
            "average": {},
            "q1": {},
            "q2": {},
            "q3": {},
            "total": {},
        }
        for benefit_code_id, values in entitlements_dict.items():
            if not values:
                stats["average"][benefit_code_id] = 0.0
                stats["q1"][benefit_code_id] = 0.0
                stats["q2"][benefit_code_id] = 0.0
                stats["q3"][benefit_code_id] = 0.0
                stats["total"][benefit_code_id] = 0.0
            else:
                arr = np.array(values)
                stats["average"][benefit_code_id] = round(float(np.mean(arr)), 2)
                stats["q1"][benefit_code_id] = round(
                    float(np.percentile(arr, 25, method="midpoint")), 2
                )
                stats["q2"][benefit_code_id] = round(
                    float(np.percentile(arr, 50, method="midpoint")), 2
                )
                stats["q3"][benefit_code_id] = round(
                    float(np.percentile(arr, 75, method="midpoint")), 2
                )
                stats["total"][benefit_code_id] = float(np.sum(arr))
        return stats
