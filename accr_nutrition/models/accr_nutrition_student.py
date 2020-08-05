import datetime
from odoo import models, fields, api, _


class accrNutritionStudent(models.Model):
    _name = 'accr.nutrition.student'
    _description = 'Student Nutrition Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [('student_unique', 'unique(student)',
                         'Can not be duplicate value for this field!')]

    name = fields.Char(string=u'Name', compute='_compute_name', readonly=True, )

    student = fields.Many2one('x_student', string=u'Student', required=True, store=True, )
    student_name = fields.Char(
        related='student.x_name', string=u'Student Name', store=False, readonly=True, )
    student_resident = fields.Boolean(
        related='student.x_studio_resident', string="Resident", store=False, readonly=True, )
    student_photo = fields.Binary(
        related='student.x_studio_student_image', string=u'Photo', store=False, readonly=True, )
    student_birth_date = fields.Date(
        related='student.x_studio_birthdate', string=u'Birth Date', store=False, readonly=True, )
    student_age = fields.Char(
        string=u'Age', compute='_compute_age', readonly=True,)
    student_gander = fields.Selection(
        related='student.x_studio_gander', string=u'Gander', store=False, readonly=True, )
    student_nationality = fields.Many2one(
        related='student.x_studio_country', string=u'Nationality', store=False, readonly=True, )
    student_medical_diagnosis = fields.Char(
        related='student.x_studio_medical_diagnosis', string=u'Medical Diagnosis', store=False, readonly=True, )
    student_diagnosis = fields.Text(
        related='student.x_studio_diagnosis', string=u'Diagnosis', store=False, readonly=True, )
    student_guardians = fields.Many2many(
        related='student.x_guardians', string=u'Guardians', store=False, readonly=True, )
    student_file_no = fields.Char(
        related='student.x_studio_file_no', string=u'File No', store=False, readonly=True, )
    student_admission_date = fields.Date(
        related='student.x_studio_joining_date', string=u'Admission Date', store=False, readonly=True, )
    student_residential_section = fields.Many2one(
        related='student.x_studio_residential_sections', string=u'Residential Section', readonly=True, )
    student_residential_room = fields.Many2one(
        related='student.x_residential_section_room', string=u'Residential Room', readonly=True, )
    student_residential_supervisor = fields.Many2one(
        related='student_residential_room.x_studio_supervisor', string=u'Residential Supervisor', readonly=True, )
    student_residential_caregiver = fields.Many2one(
        related='student_residential_room.x_studio_caregiver', string=u'Residential Caregiver', readonly=True, )
    student_medications = fields.One2many(
        related='student.x_medications', string=u'Medications', store=False, track_visibility='onchange', readonly=True, )
    student_medical_investigations = fields.One2many(related='student.x_studio_field_MSnvc', string='Medical Investigations', store=False, readonly=True, track_visibility='onchange', )
    student_hospital_visit = fields.One2many(related='student.x_studio_field_ny0LI', string='Hospital Visit', store=False, readonly=True, track_visibility='onchange', )
    student_medical_assessment = fields.One2many(related='student.x_studio_field_qswg8', string='Medical Assessment', store=False, readonly=True, track_visibility='onchange', )

    student_residential_daily_notes = fields.Many2many(
        related='student.x_section_daily_notes', string=u'Residential Notes', store=False, readonly=True, track_visibility='onchange', )
    student_leave_requests = fields.One2many(
        related="student.x_leave_requests", string=u"Leave Requests", readonly=True, store=False, track_visibility='onchange', )

    food_intolerance = fields.One2many('accr.student.food.intolerance', 'nutrition_student_food_intolerance',
                                       string=u'Food Intolerance', readonly=False, track_visibility='onchange', )
    medical_contraindication = fields.One2many('accr.student.food.intolerance', 'nutrition_student_medical_contraindication',
                                               string=u'Medical Contraindication', compute='_compute_medications_intolerance', readonly=True, track_visibility='onchange',)
    nutrition_details = fields.One2many('accr.student.nutrition.details', 'nutrition_student',
                                        string=u'Nutrition Assessment', track_visibility='onchange', )
    bca = fields.One2many('accr.bca', 'nutrition_student',
                          string="BCA", track_visibility='onchange', )
    food_preferences = fields.One2many(
        'accr.student.food.preferences', 'nutrition_student', string=u'Food Preferences', track_visibility='onchange', )

    diet = fields.Many2one('accr.diet', string=u"Diet",
                           track_visibility='onchange', )

    nutrition_plan = fields.One2many(
        'accr.nutrition.plan', 'nutrition_student', string=u'Nutrition Plan')

    follow_up = fields.Many2many('accr.nutrition.followup', 'accr_nutrition_student_followup_rel',
                                 'nutrition_student_id', 'followup_id', string=u"Follow Up", )

    student_orientation = fields.One2many(
        'accr.student.orientation', 'nutrition_student', string=u'Student Orientation', )

    meals_timetable = fields.One2many(
        'accr.meal.timetable', 'student', string="Meals Time Table", )

    info_done = fields.Boolean(string=u'Done', )

    @api.multi
    @api.depends('student')
    def _compute_name(self):
        for record in self:
            record.name = record.student.display_name

    @api.multi
    @api.depends('student_birth_date')
    def _compute_age(self):
        for record in self:
            nowdate = datetime.datetime.today()
            birthdate = record.student_birth_date
            if record.student_birth_date:
                record.student_age = str(nowdate.year - birthdate.year - (
                    (nowdate.month, nowdate.day) < (birthdate.month, birthdate.day))) + ' years'

    @api.multi
    @api.depends('student_medications')
    def _compute_medications_intolerance(self):
        for record in self:
            food_ingredientss = []
            current_date = datetime.datetime.now()
            for medication in record.student_medications:
                if current_date < medication.end_date_time:
                    medicine = medication.medicine
                    for medical_contraindication in medicine.medical_contraindication:
                        for food_ingredients in medical_contraindication.food_ingredientss:
                            food_ingredientss.append(
                                {'nutrition_student_medical_contraindication': record.id, 'food_ingredients': food_ingredients.id})
                            # record.food_intolerance.write({'nutrition_student': record.id, 'food_ingredients': food_ingredients.id})

            record.medical_contraindication = self.env['accr.student.food.intolerance'].create(
                food_ingredientss)

            #  record.student_id.write({
            #         'course_detail_ids': [[0, False, {
            #             'course_id':
            #                 record.course_id and record.course_id.id or False,
            #             'batch_id':
            #                 record.batch_id and record.batch_id.id or False,
            #         }]],
            #     })

    # @api.onchange('student_leave_requests')
    # def onchange_leave_requests(self):
    #     activity_record = {
    #         'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
    #         'res_id': self.id,
    #         'res_model_id': self.env['ir.model'].search([('model', '=', 'accr.nutrition.student')], limit=1).id,
    #         'date_deadline': datetime.datetime.now() + datetime.timedelta(days=0, hours=1),
    #         'user_id': 2,
    #         'note': 'Leave Request Created',
    #         'summary': 'Leave Request Created'
    #     }

    #     self.env['mail.activity'].create(activity_record)
