from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import mapped_column


class G2PIndividualStipendProgramRegistry(G2PRegistry):
    """Maps to g2p_individual_stipend_program_registry in the registry DB."""

    __tablename__ = "g2p_individual_stipend_program_registry"

    stipend_program_name = mapped_column(String, nullable=True)
    work_type = mapped_column(String, nullable=True)
    hours_contributed = mapped_column(Integer, nullable=True)
    contribution_from_date = mapped_column(Date, nullable=True)
    contribution_to_date = mapped_column(Date, nullable=True)
    contribution_date_range = mapped_column(Integer, nullable=True)
    record_status = mapped_column(String, nullable=True)
