from openg2p_bg_task_models.models import BeneficiaryListSummary
from sqlalchemy import Float, Integer
from sqlalchemy.orm import mapped_column


class BeneficiaryListSummaryIndividualStipendProgram(BeneficiaryListSummary):
    __tablename__ = "beneficiary_list_summary_individual_stipend_program"

    hours_contributed_mean = mapped_column(Float, nullable=True, default=0)
    part_time_count = mapped_column(Integer, nullable=True, default=0)
    full_time_count = mapped_column(Integer, nullable=True, default=0)
    social_protection_count = mapped_column(Integer, nullable=True, default=0)
