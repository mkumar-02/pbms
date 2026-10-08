from typing import Optional

from pydantic import BaseModel

from .beneficiary_list_summary import BeneficiaryListSummaryPayload


class BeneficiaryListSummaryIndividualStipendProgram(BaseModel):
    hours_contributed_mean: Optional[str] = None
    part_time_count: Optional[str] = None
    full_time_count: Optional[str] = None
    social_protection_count: Optional[str] = None


class BeneficiaryListSummaryIndividualStipendProgramPayload(BeneficiaryListSummaryPayload):
    registry_summary: BeneficiaryListSummaryIndividualStipendProgram
