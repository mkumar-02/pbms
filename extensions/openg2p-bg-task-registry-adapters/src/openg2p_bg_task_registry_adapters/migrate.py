from .models import (
    BeneficiaryListSummaryFarmer,
    BeneficiaryListSummaryHousehold,
    BeneficiaryListSummaryIndividualStipendProgram,
)


def get_models():
    return [
        BeneficiaryListSummaryFarmer,
        BeneficiaryListSummaryHousehold,
        BeneficiaryListSummaryIndividualStipendProgram,
    ]
