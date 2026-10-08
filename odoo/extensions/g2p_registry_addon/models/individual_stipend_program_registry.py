from odoo import fields, models

from .enums import STIPEND_PROGRAM_SELECTION, WORK_TYPE_SELECTION


class G2PIndividualStipendProgramRegistry(models.Model):
    _name = "g2p.individual.stipend.program.registry"
    _description = "Individual Stipend Program Registry"
    _inherit = "g2p.registry"

    stipend_program_name = fields.Selection(
        selection=STIPEND_PROGRAM_SELECTION,
        string="Stipend Program",
    )
    work_type = fields.Selection(
        selection=WORK_TYPE_SELECTION,
        string="Work Type",
    )
    hours_contributed = fields.Integer(string="Hours Contributed")
    contribution_from_date = fields.Date(string="Contribution From")
    contribution_to_date = fields.Date(string="Contribution To")
    contribution_date_range = fields.Integer(string="Contribution Date Range")
    record_status = fields.Char(string="Record Status")
