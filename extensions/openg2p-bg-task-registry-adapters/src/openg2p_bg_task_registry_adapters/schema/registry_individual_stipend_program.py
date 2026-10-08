from typing import Optional

from .registry import G2PRegistryPayload


class G2PIndividualStipendProgramRegistryPayload(G2PRegistryPayload):
    stipend_program_name: Optional[str] = None
    work_type: Optional[str] = None
    hours_contributed: Optional[int] = None
    contribution_from_date: Optional[str] = None
    contribution_to_date: Optional[str] = None
    contribution_date_range: Optional[int] = None
    record_status: Optional[str] = None
