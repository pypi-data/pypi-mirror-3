# -*- coding: utf-8 -*-
##############################################################################
#
#    GNU Health: The Free Health and Hospital Information System
#    Copyright (C) 2008-2012  Luis Falcon <lfalcon@gnusolidario.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Bool
from datetime import datetime
from trytond.pool import Pool


class GnuHealthPatient(ModelSQL, ModelView):
    'Add to the Medical patient_data class (gnuhealth.patient) the ' \
    'ophtalmologic fields.'
    _name = 'gnuhealth.patient'
    _description = __doc__

    visual_acuity_left = fields.Integer("AV L")
    visual_acuity_right = fields.Integer("AV R")
    refraction_subjective_sphere_left = fields.Float("Sph L")
    refraction_subjective_sphere_right = fields.Float("Sph R")
    refraction_subjective_cylinder_left = fields.Float("Cyl L")
    refraction_subjective_cylinder_right = fields.Float("Cyl R")
    refraction_subjective_axis_left = fields.Integer("Axis L")
    refraction_subjective_axis_right = fields.Integer("Axis R")    
    refraction_subjective_av_left = fields.Integer("AV L")    
    refraction_subjective_av_right = fields.Integer("AV R")    
    refraction_subjective_dnp_left = fields.Integer("DNP L")    
    refraction_subjective_dnp_right = fields.Integer("DNP R")    
    bicromatic_left = fields.Boolean("Bicromatic L")
    bicromatic_right = fields.Boolean("Bicromatic R")
    maximum_positive_power_left = fields.Boolean("MPAV L")
    maximum_positive_power_right = fields.Boolean("MPAV R")
    astigmatic_clock_left = fields.Boolean("Astigmatic Clock L")
    astigmatic_clock_right = fields.Boolean("Astigmatic Clock R")
    jackson_cylinder_left = fields.Boolean("Jackson Cylinder L")
    jackson_cylinder_right = fields.Boolean("Jackson Cylinder R")
    colour_test = fields.Integer("Colour Test")
    fly_test = fields.Integer("Fly Test")
    kappa_left = fields.Boolean("Kappa L")
    kappa_right = fields.Boolean("Kappa R")
    hirschberg = fields.Integer("Hirschberg")
    cover_test = fields.Boolean("Cover Test")
    ocular_motility_ductions_left = fields.Boolean("Ductions L")
    ocular_motility_ductions_right = fields.Boolean("Ductions R")
    ocular_motility_ductions_other = fields.Char("Ductions Other")
    ocular_motility_versions_left = fields.Boolean("Versions L")
    ocular_motility_versions_right = fields.Boolean("Versions R")
    ocular_motility_versions_other = fields.Char("Versions Other")
    ppc = fields.Integer("PPC")

    intraocular_preasure_left = fields.Integer("Intraocular Preasure L")
    intraocular_preasure_right = fields.Integer("Intraocular Preasure R")
    intraocular_preasure_other = fields.Char("Intraocular Preasure Other")
    bio_parpados_left = fields.Boolean("Pestana Parpados L")
    bio_parpados_right = fields.Boolean("Pestana Parpados R")
    bio_parpados_other = fields.Char("Pestana Parpados Other")
    bio_conjuntiva_left = fields.Boolean("Conjuntiva L")
    bio_conjuntiva_right = fields.Boolean("Conjuntiva R")
    bio_conjuntiva_other = fields.Char("Conjuntiva Other")
    bio_esclera_left = fields.Boolean("Esclera L")
    bio_esclera_right = fields.Boolean("Esclera R")
    bio_esclera_other = fields.Char("Esclera Other")
    bio_cornea_left = fields.Boolean("Cornea L")
    bio_cornea_right = fields.Boolean("Cornea R")
    bio_cornea_other = fields.Char("Cornea Other")
    bio_iris_left = fields.Boolean("Iris L")
    bio_iris_right = fields.Boolean("Iris R")
    bio_iris_other = fields.Char("Iris Other")
    bio_pupile_left = fields.Boolean("Pupile L")
    bio_pupile_right = fields.Boolean("Pupile R")
    bio_pupile_other = fields.Char("Pupile Other")
    bio_back_camera_left = fields.Boolean("Back Camera L")
    bio_back_camera_right = fields.Boolean("Back Camera R")
    bio_back_camera_other = fields.Char("Back Camera Other")
    bio_cristalino_left = fields.Boolean("Cristalino L")
    bio_cristalino_right = fields.Boolean("Cristalino R")
    bio_cristalino_other = fields.Char("Cristalino Other")

    direct_ophtalmo_humor_vitrio_left = fields.Boolean("Humor Vitrio L")
    direct_ophtalmo_humor_vitrio_right = fields.Boolean("Humor Vitrio R")
    direct_ophtalmo_humor_vitrio_other = fields.Char("Humor Vitrio Other")
    direct_ophtalmo_optic_nerve_left = fields.Float("Optic Nerve L")
    direct_ophtalmo_optic_nerve_right = fields.Float("Optic Nerve R")
    direct_ophtalmo_optic_nerve_other = fields.Float("Optic Nerve Other")
    direct_ophtalmo_macula_left = fields.Boolean("Macula L")
    direct_ophtalmo_macula_right = fields.Boolean("Macula R")
    direct_ophtalmo_macula_other = fields.Char("Macula Other")
    direct_ophtalmo_retina_left = fields.Boolean("Retina L")
    direct_ophtalmo_retina_right = fields.Boolean("Retina R")
    direct_ophtalmo_retina_other = fields.Char("Retina Other")
    direct_ophtalmo_dilatation = fields.Boolean("Dilatation")

    diagnostic_optometry_left = fields.Text("Izquierdo")
    diagnostic_optometry_right = fields.Text("Derecho")
    diagnostic_ophtalmology = fields.Text("Diagnostico")
    threatment_ophtalmology = fields.Text("Tratamiento")
    auxiliar_tests_ophtalmology = fields.Text("Examenes Auxiliares")
    recommendations_ophtalmology = fields.Text("Recomendaciones")

GnuHealthPatient()

