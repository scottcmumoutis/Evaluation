import csv
import math
import data
import time
from collections import OrderedDict
from itertools import islice

#MAXOBJ = 9876543210.0
#MAXVIOL = 9876543210.0
KVPEN = 1000.0 # kV penalty (p.u. already)
MVAPEN = 1000.0 #MVA penalty

#TOP_N = 10

def get_ctg_num_lines(file_name):

    ctg_start_str = '--con'
    with open(file_name, 'r') as in_file:
        lines = in_file.readlines()
    num_lines = len(lines)
    ctg_start_lines = [
        i for i in range(num_lines)
        if lines[i].startswith(ctg_start_str)]
    num_ctgs = len(ctg_start_lines)
    ctg_end_lines = [
        ctg_start_lines[i + 1]
        for i in range(num_ctgs - 1)]
    ctg_end_lines += [num_lines]
    ctg_num_lines = [
        ctg_end_lines[i] - ctg_start_lines[i]
        for i in range(num_ctgs)]
    return ctg_num_lines

class Evaluation:
    '''In per unit convention, i.e. same as the model'''

    def __init__(self):

        self.volt_pen = KVPEN
        self.pow_pen = MVAPEN
        #self.pvpq_pen = max(self.volt_pen, self.pow_pen)
        self.bus = []
        self.load = []
        self.fxsh = []
        self.gen = []
        self.line = []
        self.xfmr = []
        self.area = []
        self.swsh = []
        self.ctg = []
        
        self.bus_volt_mag_min = {}
        self.bus_volt_mag_max = {}
        self.bus_volt_mag = {}
        self.bus_volt_ang = {}
        self.bus_volt_mag_min_viol = {}
        self.bus_volt_mag_max_viol = {}
        self.bus_pow_balance_real_viol = {}
        self.bus_pow_balance_imag_viol = {}
        #self.swsh_status = {}
        #self.swsh_adm_imag_min = {}
        #self.swsh_adm_imag_max = {}
        self.bus_swsh_adm_imag_min = {}
        self.bus_swsh_adm_imag_max = {}
        self.bus_swsh_adm_imag_min_viol = {}
        self.bus_swsh_adm_imag_max_viol = {}
        self.bus_swsh_adm_imag = {}

        self.load_const_pow_real = {}
        self.load_const_pow_imag = {}
        #self.load_const_curr_real = {}
        #self.load_const_curr_imag = {}
        #self.load_const_adm_real = {}
        #self.load_const_adm_imag = {}
        self.load_pow_real = {}
        self.load_pow_imag = {}
        self.load_status = {}

        self.fxsh_adm_real = {}
        self.fxsh_adm_imag = {}
        self.fxsh_pow_real = {}
        self.fxsh_pow_imag = {}
        self.fxsh_status = {}

        #self.gen_reg_bus = {}
        self.gen_pow_real_min = {}
        self.gen_pow_real_max = {}
        self.gen_pow_imag_min = {}
        self.gen_pow_imag_max = {}
        self.gen_part_fact = {}
        self.gen_pow_real = {}
        self.gen_pow_imag = {}
        self.gen_pow_real_min_viol = {}
        self.gen_pow_real_max_viol = {}
        self.gen_pow_imag_min_viol = {}
        self.gen_pow_imag_max_viol = {}
        self.gen_status = {}

        self.line_adm_real = {}
        self.line_adm_imag = {}
        self.line_adm_ch_imag = {}
        self.line_curr_mag_max = {}
        #self.line_curr_orig_real = {}
        #self.line_curr_orig_imag = {}
        #self.line_curr_dest_real = {}
        #self.line_curr_dest_imag = {}
        self.line_pow_orig_real = {}
        self.line_pow_orig_imag = {}
        self.line_pow_dest_real = {}
        self.line_pow_dest_imag = {}
        self.line_curr_orig_mag_max_viol = {}
        self.line_curr_dest_mag_max_viol = {}
        self.line_status = {}

        self.xfmr_adm_real = {}
        self.xfmr_adm_imag = {}
        self.xfmr_adm_mag_real = {}
        self.xfmr_adm_mag_imag = {}
        self.xfmr_tap_mag = {}
        self.xfmr_tap_ang = {}
        self.xfmr_pow_mag_max = {}
        #self.xfmr_curr_orig_real = {}
        #self.xfmr_curr_orig_imag = {}
        #self.xfmr_curr_dest_real = {}
        #self.xfmr_curr_dest_imag = {}
        self.xfmr_pow_orig_real = {}
        self.xfmr_pow_orig_imag = {}
        self.xfmr_pow_dest_real = {}
        self.xfmr_pow_dest_imag = {}
        self.xfmr_pow_orig_mag_max_viol = {}
        self.xfmr_pow_dest_mag_max_viol = {}
        self.xfmr_status = {}

        self.swsh_adm_imag_min = {}
        self.swsh_adm_imag_max = {}
        self.swsh_status = {}

        self.ctg_label = ""

        self.ctg_bus_volt_mag = {}
        self.ctg_bus_volt_ang = {}
        self.ctg_bus_volt_mag_max_viol = {}
        self.ctg_bus_volt_mag_min_viol = {}
        self.ctg_bus_pow_balance_real_viol = {}
        self.ctg_bus_pow_balance_imag_viol = {}
        self.ctg_bus_swsh_adm_imag = {}
        self.ctg_bus_swsh_adm_imag_min_viol = {}
        self.ctg_bus_swsh_adm_imag_max_viol = {}

        self.ctg_load_pow_real = {}
        self.ctg_load_pow_imag = {}

        self.ctg_fxsh_pow_real = {}
        self.ctg_fxsh_pow_imag = {}

        self.ctg_gen_active = {}
        #self.ctg_gen_pow_fact = {}
        self.ctg_gen_pow_real = {}
        self.ctg_gen_pow_imag = {}
        self.ctg_gen_pow_real_min_viol = {}
        self.ctg_gen_pow_real_max_viol = {}
        self.ctg_gen_pow_imag_min_viol = {}
        self.ctg_gen_pow_imag_max_viol = {}

        #self.ctg_line_curr_orig_real = {}
        #self.ctg_line_curr_orig_imag = {}
        #self.ctg_line_curr_dest_real = {}
        #self.ctg_line_curr_dest_imag = {}
        self.ctg_line_pow_orig_real = {}
        self.ctg_line_pow_orig_imag = {}
        self.ctg_line_pow_dest_real = {}
        self.ctg_line_pow_dest_imag = {}
        self.ctg_line_curr_orig_mag_max_viol = {}
        self.ctg_line_curr_dest_mag_max_viol = {}
        self.ctg_line_active = {}

        #self.ctg_xfmr_curr_orig_real = {}
        #self.ctg_xfmr_curr_orig_imag = {}
        #self.ctg_xfmr_curr_dest_real = {}
        #self.ctg_xfmr_curr_dest_imag = {}
        self.ctg_xfmr_pow_orig_real = {}
        self.ctg_xfmr_pow_orig_imag = {}
        self.ctg_xfmr_pow_dest_real = {}
        self.ctg_xfmr_pow_dest_imag = {}
        self.ctg_xfmr_pow_orig_mag_max_viol = {}
        self.ctg_xfmr_pow_dest_mag_max_viol = {}
        self.ctg_xfmr_active = {}

        #self.area_ctg_affected = {}
        #self.area_ctg_pow_real_change = {}

        self.gen_num_pl = {}
        self.gen_pl_x = {}
        self.gen_pl_y = {}

    def set_data(self, data):
        ''' set values from the data object
        convert to per unit (p.u.) convention'''

        self.bus = [r.i for r in data.raw.buses.values()]
        self.load = [(r.i,r.id) for r in data.raw.loads.values()]
        self.fxsh = [(r.i,r.id) for r in data.raw.fixed_shunts.values()]
        self.gen = [(r.i,r.id) for r in data.raw.generators.values()]
        self.line = [(r.i,r.j,r.ckt) for r in data.raw.nontransformer_branches.values()]
        self.xfmr = [(r.i,r.j,r.ckt) for r in data.raw.transformers.values()]
        self.swsh = [r.i for r in data.raw.switched_shunts.values()]
        self.area = [r.i for r in data.raw.areas.values()]
        self.ctg = [r.label for r in data.con.contingencies.values()]
        
        self.base_mva = data.raw.case_identification.sbase

        self.bus_base_kv = {
            r.i:r.baskv
            for r in data.raw.buses.values()}
        self.bus_volt_mag_max = {
            r.i:r.nvhi
            for r in data.raw.buses.values()}
        self.bus_volt_mag_min = {
            r.i:r.nvlo
            for r in data.raw.buses.values()}
        #self.ctg_bus_volt_mag_max = {
        #    r.i:r.evhi
        #    for r in data.raw.buses.values()}
        #self.ctg_bus_volt_mag_min = {
        #    r.i:r.evlo
        #    for r in data.raw.buses.values()}
        self.bus_area = {
            r.i:r.area
            for r in data.raw.buses.values()}

        self.load_const_pow_real = {
            (r.i,r.id):(r.pl/self.base_mva)
            for r in data.raw.loads.values()}
        self.load_const_pow_imag = {
            (r.i,r.id):(r.ql/self.base_mva)
            for r in data.raw.loads.values()}
        self.load_status = {
            (r.i,r.id):r.status
            for r in data.raw.loads.values()}

        self.fxsh_adm_real = {
            (r.i,r.id):(r.gl/self.base_mva)
            for r in data.raw.fixed_shunts.values()}
        self.fxsh_adm_imag = {
            (r.i,r.id):(r.bl/self.base_mva)
            for r in data.raw.fixed_shunts.values()}
        self.fxsh_status = {
            (r.i,r.id):r.status
            for r in data.raw.fixed_shunts.values()}

        self.gen_status = {
            (r.i,r.id):r.stat
            for r in data.raw.generators.values()}
        self.gen_pow_imag_max = {
            (r.i,r.id):(r.qt/self.base_mva)
            for r in data.raw.generators.values()}
        self.gen_pow_imag_min = {
            (r.i,r.id):(r.qb/self.base_mva)
            for r in data.raw.generators.values()}
        self.gen_pow_real_max = {
            (r.i,r.id):(r.pt/self.base_mva)
            for r in data.raw.generators.values()}
        self.gen_pow_real_min = {
            (r.i,r.id):(r.pb/self.base_mva)
            for r in data.raw.generators.values()}
        self.gen_part_fact = {
            (r.i,r.id):r.r
            for r in data.inl.generator_inl_records.values()}

        self.line_adm_real = {
            (r.i,r.j,r.ckt):(r.r/(r.r**2.0 + r.x**2.0))
            for r in data.raw.nontransformer_branches.values()}
        self.line_adm_imag = {
            (r.i,r.j,r.ckt):(-r.x/(r.r**2.0 + r.x**2.0))
            for r in data.raw.nontransformer_branches.values()}
        self.line_adm_ch_imag = {
            (r.i,r.j,r.ckt):r.b
            for r in data.raw.nontransformer_branches.values()}
        self.line_curr_mag_max = {
            (r.i,r.j,r.ckt):(r.ratea/self.base_mva) # todo - normalize by bus base kv???
            for r in data.raw.nontransformer_branches.values()}
        #self.ctg_line_curr_mag_max = {
        #    (r.i,r.j,r.ckt):(r.ratec/self.base_mva) # todo - normalize by bus base kv???
        #    for r in data.raw.nontransformer_branches.values()}
        self.line_status = {
            (r.i,r.j,r.ckt):r.st
            for r in data.raw.nontransformer_branches.values()}

        self.xfmr_adm_real = {
            (r.i,r.j,r.ckt):(r.r12 / (r.r12**2.0 + r.x12**2.0))
            for r in data.raw.transformers.values()}
        self.xfmr_adm_imag = {
            (r.i,r.j,r.ckt):(-r.x12 / (r.r12**2.0 + r.x12**2.0))
            for r in data.raw.transformers.values()}
        self.xfmr_adm_mag_real = {
            (r.i,r.j,r.ckt):r.mag1 # todo normalize?
            for r in data.raw.transformers.values()}
        self.xfmr_adm_mag_imag = {
            (r.i,r.j,r.ckt):r.mag2 # todo normalize?
            for r in data.raw.transformers.values()}
        self.xfmr_tap_mag = {
            (r.i,r.j,r.ckt):(r.windv1/r.windv2)
            for r in data.raw.transformers.values()}
        self.xfmr_tap_ang = {
            (r.i,r.j,r.ckt):(r.ang1*math.pi/180.0)
            for r in data.raw.transformers.values()}
        self.xfmr_pow_mag_max = {
            (r.i,r.j,r.ckt):(r.rata1/self.base_mva) # todo check normalization
            for r in data.raw.transformers.values()}
        #self.ctg_xfmr_pow_mag_max = {
        #    (r.i,r.j,r.ckt):(r.ratc1/self.base_mva) # todo check normalization
        #    for r in data.raw.transformers.values()}
        self.xfmr_status = {
            (r.i,r.j,r.ckt):r.stat
            for r in data.raw.transformers.values()}

        # swsh
        self.swsh_status = {
            r.i:r.stat
            for r in data.raw.switched_shunts.values()}
        self.swsh_adm_imag_max = {
            r.i:((max(0.0, r.n1 * r.b1) +
                  max(0.0, r.n2 * r.b2) +
                  max(0.0, r.n3 * r.b3) +
                  max(0.0, r.n4 * r.b4) +
                  max(0.0, r.n5 * r.b5) +
                  max(0.0, r.n6 * r.b6) +
                  max(0.0, r.n7 * r.b7) +
                  max(0.0, r.n8 * r.b8)) / self.base_mva) # todo normalize ?
            for r in data.raw.switched_shunts.values()}
        self.swsh_adm_imag_min = {
            r.i:((min(0.0, r.n1 * r.b1) +
                  min(0.0, r.n2 * r.b2) +
                  min(0.0, r.n3 * r.b3) +
                  min(0.0, r.n4 * r.b4) +
                  min(0.0, r.n5 * r.b5) +
                  min(0.0, r.n6 * r.b6) +
                  min(0.0, r.n7 * r.b7) +
                  min(0.0, r.n8 * r.b8)) / self.base_mva) # todo normalize ?
            for r in data.raw.switched_shunts.values()}

        # todo clean up maybe
        # defines some attributes that need to be initialized above
        # piecewise linear cost functions
        #'''
        for r in data.rop.generator_dispatch_records.values():
            r_bus = r.bus
            r_genid = r.genid
            r_dsptbl = r.dsptbl
            s = data.rop.active_power_dispatch_records[r_dsptbl]
            r_ctbl = s.ctbl
            t = data.rop.piecewise_linear_cost_functions[r_ctbl]
            r_npairs = t.npairs
            self.gen_num_pl[(r_bus,r_genid)] = r_npairs
            for i in range(r_npairs):
                key = (r_bus, r_genid, i + 1)
                #gen_pl.add_record(key)
                self.gen_pl_x[key] = t.points[i].x / self.base_mva
                self.gen_pl_y[key] = t.points[i].y            
        #'''

        # maps from buses to components
        self.bus_load = {
            i:[k for k in self.load if k[0] == i]
            for i in self.bus}
        self.bus_fxsh = {
            i:[k for k in self.fxsh if k[0] == i]
            for i in self.bus}
        self.bus_gen = {
            i:[k for k in self.gen if k[0] == i]
            for i in self.bus}
        self.bus_line_orig = {
            i:[k for k in self.line if k[0] == i]
            for i in self.bus}
        self.bus_line_dest = {
            i:[k for k in self.line if k[1] == i]
            for i in self.bus}
        self.bus_xfmr_orig = {
            i:[k for k in self.xfmr if k[0] == i]
            for i in self.bus}
        self.bus_xfmr_dest = {
            i:[k for k in self.xfmr if k[1] == i]
            for i in self.bus}

        self.bus_swsh_adm_imag_max = {i:0.0 for i in self.bus}
        self.bus_swsh_adm_imag_max.update(
            {i:self.swsh_adm_imag_max[i]
             for i in self.swsh if self.swsh_status[i]})
        self.bus_swsh_adm_imag_min = {i:0.0 for i in self.bus}
        self.bus_swsh_adm_imag_min.update(
            {i:self.swsh_adm_imag_min[i]
             for i in self.swsh if self.swsh_status[i]})
        
        # contingency records
        # TODO - stll need gen_ctg_part_fact
        # and area_ctg_affected will need to be done more carefully
        self.gen_area = {r:self.bus_area[r[0]] for r in self.gen}
        self.area_gens = {a:set() for a in self.area}
        for i in self.gen:
            self.area_gens[self.gen_area[i]].add(i)
        self.ctg_gens_out = {k:set() for k in self.ctg}
        self.ctg_lines_out = {k:set() for k in self.ctg}
        self.ctg_xfmrs_out = {k:set() for k in self.ctg}
        self.ctg_areas_affected = {k:set() for k in self.ctg}
        for r in data.con.contingencies.values():
            for e in r.branch_out_events:
                if (e.i, e.j, e.ckt) in data.raw.nontransformer_branches.keys():
                    self.ctg_lines_out[r.label].add((e.i, e.j, e.ckt))
                    self.ctg_areas_affected[r.label].add(self.bus_area[e.i])
                    self.ctg_areas_affected[r.label].add(self.bus_area[e.j])
                if (e.i, e.j, 0, e.ckt) in data.raw.transformers.keys():
                    self.ctg_xfmrs_out[r.label].add((e.i, e.j, e.ckt))
                    self.ctg_areas_affected[r.label].add(self.bus_area[e.i])
                    self.ctg_areas_affected[r.label].add(self.bus_area[e.j])
            for e in r.generator_out_events:
                self.ctg_gens_out[r.label].add((e.i, e.id))
                self.ctg_areas_affected[r.label].add(self.bus_area[e.i])
        #self.gen_ctg_participating = {
        #    (r[0],r[1],k):(
        #        1 if (
        #            self.gen_ctg_active[(r[0],r[1],k)] and
        #            self.area_ctg_affected[(self.gen_area[r],k)])
        #        else 0)
        #    for r in self.gen
        #    for k in self.ctg}

        # generator real power emergency min/max
        # todo read from data
        #self.gen_pow_real_emerg_max = {
        #    #(r.i,r.id):(r.pt/self.base_mva)
        #    (r.i,r.id):float("inf")
        #    for r in data.raw.generators.values()}
        #self.gen_pow_real_emerg_min = {
        #    #(r.i,r.id):(r.pb/self.base_mva)
        #    (r.i,r.id):(-float("inf"))
        #    for r in data.raw.generators.values()}    

    def set_params(self):
        '''set parameters, e.g. tolerances, penalties, and convert to PU'''

        self.volt_pen = self.volt_pen # starts in p.u. by convention
        self.pow_pen = self.base_mva * self.pow_pen
        #self.pvpq_pen = max(self.volt_pen, self.pow_pen)
        
    def set_solution1(self, solution1):
        ''' set values from the solution objects
        convert to per unit (p.u.) convention'''

        self.bus_volt_mag = {
            i:solution1.bus_volt_mag[i]
            for i in self.bus}
        self.bus_volt_ang = {
            i:solution1.bus_volt_ang[i] * math.pi / 180.0
            for i in self.bus}
        self.bus_swsh_adm_imag = {
            i:solution1.bus_swsh_adm_imag[i] / self.base_mva
            for i in self.bus}
        self.gen_pow_real = {
            i:solution1.gen_pow_real[i] / self.base_mva
            for i in self.gen}
        self.gen_pow_imag = {
            i:solution1.gen_pow_imag[i] / self.base_mva
            for i in self.gen}
    
    def set_solution2(self, solution2):
        ''' set values from the solution objects
        convert to per unit (p.u.) convention'''

        self.ctg_label = solution2.ctg_label
        self.ctg_bus_volt_mag = {
            i:solution2.bus_volt_mag[i]
            for i in self.bus}
        self.ctg_bus_volt_ang = {
            i:solution2.bus_volt_ang[i] * math.pi / 180.0
            for i in self.bus}
        self.ctg_bus_swsh_adm_imag = {
            i:solution2.bus_swsh_adm_imag[i] / self.base_mva
            for i in self.bus}
        self.ctg_gen_pow_real = {
            i:solution2.gen_pow_real[i] / self.base_mva
            for i in self.gen}
        self.ctg_gen_pow_imag = {
            i:solution2.gen_pow_imag[i] / self.base_mva
            for i in self.gen}
        self.ctg_pow_real_change = solution2.pow_real_change / self.base_mva

    def set_ctg_data(self):

        self.ctg_gen_active = {
            i:self.gen_status[i]
            for i in self.gen}
        self.ctg_gen_active.update(
            {i:0 for i in self.ctg_gens_out[self.ctg_label]})
        self.ctg_line_active = {
            i:self.line_status[i]
            for i in self.line}
        self.ctg_line_active.update(
            {i:0 for i in self.ctg_lines_out[self.ctg_label]})
        self.ctg_xfmr_active = {
            i:self.xfmr_status[i]
            for i in self.xfmr}
        self.ctg_xfmr_active.update(
            {i:0 for i in self.ctg_xfmrs_out[self.ctg_label]})
        self.ctg_gen_participating = {i:0 for i in self.gen}
        self.ctg_gen_participating.update(
            {i:self.ctg_gen_active[i]
             for a in self.ctg_areas_affected[self.ctg_label]
             for i in self.area_gens[a]})

    def write_header(self, det_name):
        """write header line for detailed output"""

        with open(det_name, 'wb') as out:
            csv_writer = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(
                ['ctg', 'infeas', 'pen', 'cost', 'obj',
                 'vmax-idx',
                 'vmax-val',
                 'vmin-idx',
                 'vmin-val',
                 'bmax-idx',
                 'bmax-val',
                 'bmin-idx',
                 'bmin-val',
                 'pbal-idx',
                 'pbal-val',
                 'qbal-idx',
                 'qbal-val',
                 'pgmax-idx',
                 'pgmax-val',
                 'pgmin-idx',
                 'pgmin-val',
                 'qgmax-idx',
                 'qgmax-val',
                 'qgmin-idx',
                 'qgmin-val',
                 'qvg1-idx',
                 'qvg1-val',
                 'qvg2-idx',
                 'qvg2-val',
                 'lineomax-idx',
                 'lineomax-val',
                 'linedmax-idx',
                 'linedmax-val',
                 'xfmromax-idx',
                 'xfmromax-val',
                 'xfmrdmax-idx',
                 'xfmrdmax-val',
             ])

    def write_base(self, det_name):
        """write detail of base case evaluation"""

        with open(det_name, 'ab') as out:
            csv_writer = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(
                ['', self.infeas, self.penalty, self.cost, self.obj,
                 self.max_bus_volt_mag_max_viol[0],
                 self.max_bus_volt_mag_max_viol[1],
                 self.max_bus_volt_mag_min_viol[0],
                 self.max_bus_volt_mag_min_viol[1],
                 self.max_bus_swsh_adm_imag_max_viol[0],
                 self.max_bus_swsh_adm_imag_max_viol[1],
                 self.max_bus_swsh_adm_imag_min_viol[0],
                 self.max_bus_swsh_adm_imag_min_viol[1],
                 self.max_bus_pow_balance_real_viol[0],
                 self.max_bus_pow_balance_real_viol[1],
                 self.max_bus_pow_balance_imag_viol[0],
                 self.max_bus_pow_balance_imag_viol[1],
                 self.max_gen_pow_real_max_viol[0],
                 self.max_gen_pow_real_max_viol[1],
                 self.max_gen_pow_real_min_viol[0],
                 self.max_gen_pow_real_min_viol[1],
                 self.max_gen_pow_imag_max_viol[0],
                 self.max_gen_pow_imag_max_viol[1],
                 self.max_gen_pow_imag_min_viol[0],
                 self.max_gen_pow_imag_min_viol[1],
                 None,
                 0.0,
                 None,
                 0.0,
                 self.max_line_curr_orig_mag_max_viol[0],
                 self.max_line_curr_orig_mag_max_viol[1],
                 self.max_line_curr_dest_mag_max_viol[0],
                 self.max_line_curr_dest_mag_max_viol[1],
                 self.max_xfmr_pow_orig_mag_max_viol[0],
                 self.max_xfmr_pow_orig_mag_max_viol[1],
                 self.max_xfmr_pow_dest_mag_max_viol[0],
                 self.max_xfmr_pow_dest_mag_max_viol[1],
                 ])

    def write_ctg(self, det_name):
        """write detail of ctg evaluation"""        

        with open(det_name, 'ab') as out:
            csv_writer = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(
                [self.ctg_label, self.ctg_infeas, self.ctg_penalty, 0.0, self.obj,
                 self.ctg_max_bus_volt_mag_max_viol[0],
                 self.ctg_max_bus_volt_mag_max_viol[1],
                 self.ctg_max_bus_volt_mag_min_viol[0],
                 self.ctg_max_bus_volt_mag_min_viol[1],
                 self.ctg_max_bus_swsh_adm_imag_max_viol[0],
                 self.ctg_max_bus_swsh_adm_imag_max_viol[1],
                 self.ctg_max_bus_swsh_adm_imag_min_viol[0],
                 self.ctg_max_bus_swsh_adm_imag_min_viol[1],
                 self.ctg_max_bus_pow_balance_real_viol[0],
                 self.ctg_max_bus_pow_balance_real_viol[1],
                 self.ctg_max_bus_pow_balance_imag_viol[0],
                 self.ctg_max_bus_pow_balance_imag_viol[1],
                 self.ctg_max_gen_pow_real_max_viol[0],
                 self.ctg_max_gen_pow_real_max_viol[1],
                 self.ctg_max_gen_pow_real_min_viol[0],
                 self.ctg_max_gen_pow_real_min_viol[1],
                 self.ctg_max_gen_pow_imag_max_viol[0],
                 self.ctg_max_gen_pow_imag_max_viol[1],
                 self.ctg_max_gen_pow_imag_min_viol[0],
                 self.ctg_max_gen_pow_imag_min_viol[1],
                 self.ctg_max_gen_pvpq1_viol[0],
                 self.ctg_max_gen_pvpq1_viol[1],
                 self.ctg_max_gen_pvpq2_viol[0],
                 self.ctg_max_gen_pvpq2_viol[1],
                 self.ctg_max_line_curr_orig_mag_max_viol[0],
                 self.ctg_max_line_curr_orig_mag_max_viol[1],
                 self.ctg_max_line_curr_dest_mag_max_viol[0],
                 self.ctg_max_line_curr_dest_mag_max_viol[1],
                 self.ctg_max_xfmr_pow_orig_mag_max_viol[0],
                 self.ctg_max_xfmr_pow_orig_mag_max_viol[1],
                 self.ctg_max_xfmr_pow_dest_mag_max_viol[0],
                 self.ctg_max_xfmr_pow_dest_mag_max_viol[1],
                 ])

    def eval_base(self):
        """evaluate base case violations"""

        self.eval_cost()
        self.eval_bus_volt_viol()
        self.eval_load_pow()
        self.eval_fxsh_pow()
        self.eval_gen_pow_viol()
        self.eval_line_pow()
        self.eval_line_curr_viol()
        self.eval_xfmr_pow()
        self.eval_xfmr_pow_viol()
        self.eval_bus_swsh_adm_imag_viol()
        self.eval_bus_swsh_pow()
        self.eval_bus_pow_balance()
        self.compute_detail()
        self.eval_infeas()
        self.eval_penalty()
        self.eval_obj()

    def eval_ctg(self):

        self.eval_ctg_bus_volt_viol()
        self.eval_ctg_load_pow()
        self.eval_ctg_fxsh_pow()
        self.eval_ctg_gen_pow_real()
        #self.eval_ctg_gen_pow_real_viol()
        self.eval_ctg_gen_pow_imag_viol()
        self.eval_ctg_line_pow()
        self.eval_ctg_line_curr_viol()
        self.eval_ctg_xfmr_pow()
        self.eval_ctg_xfmr_pow_viol()
        self.eval_ctg_bus_swsh_adm_imag_viol()
        self.eval_ctg_bus_swsh_pow()
        self.eval_ctg_bus_pow_balance()
        self.eval_ctg_gen_pvpq_viol()
        self.compute_ctg_detail()
        self.eval_ctg_infeas()
        self.eval_ctg_penalty()
        self.eval_ctg_update_obj()

    def eval_ctg_update_obj(self):

        self.obj += self.ctg_penalty
    
    def eval_cost(self):
        # todo: what if gen_pow_real falls outside of domain of definition
        # of cost function?
        # maybe just assign maximum cost value as the cost

        self.gen_pl_cost = {}
        self.gen_cost = {
            k:0.0
            for k in self.gen}
        for k in self.gen:
            if self.gen_status[k]:
                y_value = self.gen_pl_y[(k[0], k[1], self.gen_num_pl[k])]
                slope = 0.0
                x_change = 0.0
                pl = self.gen_num_pl[k]
                for i in range(1, self.gen_num_pl[k]):
                    if self.gen_pow_real[k] <= self.gen_pl_x[(k[0], k[1], i + 1)]:
                        y_value = self.gen_pl_y[(k[0], k[1], i)]
                        if self.gen_pl_x[(k[0], k[1], i + 1)] > self.gen_pl_x[(k[0], k[1], i)]:
                            slope = (
                                (self.gen_pl_y[(k[0], k[1], i + 1)] -
                                 self.gen_pl_y[(k[0], k[1], i)]) /
                                (self.gen_pl_x[(k[0], k[1], i + 1)] -
                                 self.gen_pl_x[(k[0], k[1], i)]))
                            x_change = (
                                self.gen_pow_real[k] -
                                self.gen_pl_x[(k[0], k[1], i)])
                        pl = i
                        break
                self.gen_cost[k] = y_value + slope * x_change
        self.cost = sum([0.0] + self.gen_cost.values())

    def eval_bus_volt_viol(self):

        self.bus_volt_mag_min_viol = {
            k:max(0.0, self.bus_volt_mag_min[k] - self.bus_volt_mag[k])
            for k in self.bus}
        self.bus_volt_mag_max_viol = {
            k:max(0.0, self.bus_volt_mag[k] - self.bus_volt_mag_max[k])
            for k in self.bus}

    def eval_load_pow(self):

        self.load_pow_real = {
            k:(self.load_const_pow_real[k]
               if self.load_status[k] else 0.0)
            for k in self.load}
        self.load_pow_imag = {
            k:(self.load_const_pow_imag[k]
               if self.load_status[k] else 0.0) 
            for k in self.load}

    def eval_fxsh_pow(self):

        self.fxsh_pow_real = {
            k:(self.fxsh_adm_real[k] * self.bus_volt_mag[k[0]]**2.0
               if self.fxsh_status[k] else 0.0)
            for k in self.fxsh}
        self.fxsh_pow_imag = {
            k:(-self.fxsh_adm_imag[k] * self.bus_volt_mag[k[0]]**2.0
               if self.fxsh_status[k] else 0.0)
            for k in self.fxsh}

    def eval_gen_pow_viol(self):

        self.gen_pow_real_min_viol = {
            k:max(0.0, (self.gen_pow_real_min[k] if self.gen_status[k] else 0.0) - self.gen_pow_real[k])
            for k in self.gen}
        self.gen_pow_real_max_viol = {
            k:max(0.0, self.gen_pow_real[k] - (self.gen_pow_real_max[k] if self.gen_status[k] else 0.0))
            for k in self.gen}
        self.gen_pow_imag_min_viol = {
            k:max(0.0, (self.gen_pow_imag_min[k] if self.gen_status[k] else 0.0) - self.gen_pow_imag[k])
            for k in self.gen}
        self.gen_pow_imag_max_viol = {
            k:max(0.0, self.gen_pow_imag[k] - (self.gen_pow_imag_max[k] if self.gen_status[k] else 0.0))
            for k in self.gen}

    """
    def eval_line_curr(self):

        self.line_curr_orig_real = {
            k:(
                self.line_adm_real[k] *
                (
                    self.bus_volt_mag[k[0]] * math.cos(self.bus_volt_ang[k[0]]) -
                    self.bus_volt_mag[k[1]] * math.cos(self.bus_volt_ang[k[1]])) -
                self.line_adm_imag[k] *
                (
                    self.bus_volt_mag[k[0]] * math.sin(self.bus_volt_ang[k[0]]) -
                    self.bus_volt_mag[k[1]] * math.sin(self.bus_volt_ang[k[1]])) -
                0.5 * self.line_adm_ch_imag[k] * self.bus_volt_mag[k[0]] * math.sin(self.bus_volt_ang[k[0]])
                if self.line_status[k] else 0.0)
            for k in self.line}
        self.line_curr_orig_imag = {
            k:(
                self.line_adm_real[k] *
                (
                    self.bus_volt_mag[k[0]] * math.sin(self.bus_volt_ang[k[0]]) -
                    self.bus_volt_mag[k[1]] * math.sin(self.bus_volt_ang[k[1]])) +
                self.line_adm_imag[k] *
                (
                    self.bus_volt_mag[k[0]] * math.cos(self.bus_volt_ang[k[0]]) -
                    self.bus_volt_mag[k[1]] * math.cos(self.bus_volt_ang[k[1]])) +
                0.5 * self.line_adm_ch_imag[k] * self.bus_volt_mag[k[0]] * math.cos(self.bus_volt_ang[k[0]])
                if self.line_status[k] else 0.0)
            for k in self.line}
        self.line_curr_dest_real = {
            k:(
                self.line_adm_real[k] *
                (
                    self.bus_volt_mag[k[1]] * math.cos(self.bus_volt_ang[k[1]]) -
                    self.bus_volt_mag[k[0]] * math.cos(self.bus_volt_ang[k[0]])) -
                self.line_adm_imag[k] *
                (
                    self.bus_volt_mag[k[1]] * math.sin(self.bus_volt_ang[k[1]]) -
                    self.bus_volt_mag[k[0]] * math.sin(self.bus_volt_ang[k[0]])) -
                0.5 * self.line_adm_ch_imag[k] * self.bus_volt_mag[k[1]] * math.sin(self.bus_volt_ang[k[1]])
                if self.line_status[k] else 0.0)
            for k in self.line}
        self.line_curr_dest_imag = {
            k:(
                self.line_adm_real[k] *
                (
                    self.bus_volt_mag[k[1]] * math.sin(self.bus_volt_ang[k[1]]) -
                    self.bus_volt_mag[k[0]] * math.sin(self.bus_volt_ang[k[0]])) +
                self.line_adm_imag[k] *
                (
                    self.bus_volt_mag[k[1]] * math.cos(self.bus_volt_ang[k[1]]) -
                    self.bus_volt_mag[k[0]] * math.cos(self.bus_volt_ang[k[0]])) +
                0.5 * self.line_adm_ch_imag[k] * self.bus_volt_mag[k[1]] * math.cos(self.bus_volt_ang[k[1]])
                if self.line_status[k] else 0.0)
            for k in self.line}
    """

    def eval_line_pow(self):

        self.line_pow_orig_real = {
            k:( self.line_adm_real[k] * self.bus_volt_mag[k[0]]**2.0 +
                ( - self.line_adm_real[k] * math.cos(self.bus_volt_ang[k[0]] - self.bus_volt_ang[k[1]])
                  - self.line_adm_imag[k] * math.sin(self.bus_volt_ang[k[0]] - self.bus_volt_ang[k[1]])) *
                self.bus_volt_mag[k[0]] * self.bus_volt_mag[k[1]]
                if self.line_status[k] else 0.0)
            for k in self.line}
        self.line_pow_orig_imag = {
            k:( - (self.line_adm_imag[k] + 0.5 * self.line_adm_ch_imag[k]) * self.bus_volt_mag[k[0]]**2.0 +
                (   self.line_adm_imag[k] * math.cos(self.bus_volt_ang[k[0]] - self.bus_volt_ang[k[1]])
                  - self.line_adm_real[k] * math.sin(self.bus_volt_ang[k[0]] - self.bus_volt_ang[k[1]])) *
                self.bus_volt_mag[k[0]] * self.bus_volt_mag[k[1]]
                if self.line_status[k] else 0.0)
            for k in self.line}
        self.line_pow_dest_real = {
            k:( self.line_adm_real[k] * self.bus_volt_mag[k[1]]**2.0 +
                ( - self.line_adm_real[k] * math.cos(self.bus_volt_ang[k[1]] - self.bus_volt_ang[k[0]])
                  - self.line_adm_imag[k] * math.sin(self.bus_volt_ang[k[1]] - self.bus_volt_ang[k[0]])) *
                self.bus_volt_mag[k[0]] * self.bus_volt_mag[k[1]]
                if self.line_status[k] else 0.0)
            for k in self.line}
        self.line_pow_dest_imag = {
            k:( - (self.line_adm_imag[k] + 0.5 * self.line_adm_ch_imag[k]) * self.bus_volt_mag[k[1]]**2.0 +
                (   self.line_adm_imag[k] * math.cos(self.bus_volt_ang[k[1]] - self.bus_volt_ang[k[0]])
                  - self.line_adm_real[k] * math.sin(self.bus_volt_ang[k[1]] - self.bus_volt_ang[k[0]])) *
                self.bus_volt_mag[k[0]] * self.bus_volt_mag[k[1]]
                if self.line_status[k] else 0.0)
            for k in self.line}

    def eval_line_curr_viol(self):

        self.line_curr_orig_mag_max_viol = {
            k:max(
                0.0,
                (self.line_pow_orig_real[k]**2.0 +
                 self.line_pow_orig_imag[k]**2.0)**0.5 -
                self.line_curr_mag_max[k] * self.bus_volt_mag[k[0]])
            for k in self.line}
        self.line_curr_dest_mag_max_viol = {
            k:max(
                0.0,
                (self.line_pow_dest_real[k]**2.0 +
                 self.line_pow_dest_imag[k]**2.0)**0.5 -
                self.line_curr_mag_max[k] * self.bus_volt_mag[k[1]])
            for k in self.line}

    def eval_xfmr_pow(self):

        self.xfmr_pow_orig_real = {
            k:( (self.xfmr_adm_real[k] / self.xfmr_tap_mag[k]**2.0 + self.xfmr_adm_mag_real[k]) * self.bus_volt_mag[k[0]]**2.0 +
                ( - self.xfmr_adm_real[k] / self.xfmr_tap_mag[k] * math.cos(self.bus_volt_ang[k[0]] - self.bus_volt_ang[k[1]] - self.xfmr_tap_ang[k])
                  - self.xfmr_adm_imag[k] / self.xfmr_tap_mag[k] * math.sin(self.bus_volt_ang[k[0]] - self.bus_volt_ang[k[1]] - self.xfmr_tap_ang[k])) *
                self.bus_volt_mag[k[0]] * self.bus_volt_mag[k[1]]
                if self.xfmr_status[k] else 0.0)
            for k in self.xfmr}
        self.xfmr_pow_orig_imag = {
            k:( - (self.xfmr_adm_imag[k] / self.xfmr_tap_mag[k]**2.0 + self.xfmr_adm_mag_imag[k]) * self.bus_volt_mag[k[0]]**2.0 +
                (   self.xfmr_adm_imag[k] / self.xfmr_tap_mag[k] * math.cos(self.bus_volt_ang[k[0]] - self.bus_volt_ang[k[1]] - self.xfmr_tap_ang[k])
                    - self.xfmr_adm_real[k] / self.xfmr_tap_mag[k] * math.sin(self.bus_volt_ang[k[0]] - self.bus_volt_ang[k[1]] - self.xfmr_tap_ang[k])) *
                self.bus_volt_mag[k[0]] * self.bus_volt_mag[k[1]]
                if self.xfmr_status[k] else 0.0)
            for k in self.xfmr}
        self.xfmr_pow_dest_real = {
            k:( self.xfmr_adm_real[k] * self.bus_volt_mag[k[1]]**2.0 +
                ( - self.xfmr_adm_real[k] / self.xfmr_tap_mag[k] * math.cos(self.bus_volt_ang[k[1]] - self.bus_volt_ang[k[0]] + self.xfmr_tap_ang[k])
                  - self.xfmr_adm_imag[k] / self.xfmr_tap_mag[k] * math.sin(self.bus_volt_ang[k[1]] - self.bus_volt_ang[k[0]] + self.xfmr_tap_ang[k])) *
                self.bus_volt_mag[k[0]] * self.bus_volt_mag[k[1]]
                if self.xfmr_status[k] else 0.0)
            for k in self.xfmr}
        self.xfmr_pow_dest_imag = {
            k:( - self.xfmr_adm_imag[k] * self.bus_volt_mag[k[1]]**2.0 +
                (   self.xfmr_adm_imag[k] / self.xfmr_tap_mag[k] * math.cos(self.bus_volt_ang[k[1]] - self.bus_volt_ang[k[0]] + self.xfmr_tap_ang[k])
                    - self.xfmr_adm_real[k] / self.xfmr_tap_mag[k] * math.sin(self.bus_volt_ang[k[1]] - self.bus_volt_ang[k[0]] + self.xfmr_tap_ang[k])) *
                self.bus_volt_mag[k[0]] * self.bus_volt_mag[k[1]]
                if self.xfmr_status[k] else 0.0)
            for k in self.xfmr}

    def eval_xfmr_pow_viol(self):

        self.xfmr_pow_orig_mag_max_viol = {
            k:max(
                0.0,
                (self.xfmr_pow_orig_real[k]**2.0 +
                 self.xfmr_pow_orig_imag[k]**2.0)**0.5 -
                self.xfmr_pow_mag_max[k])
            for k in self.xfmr}
        self.xfmr_pow_dest_mag_max_viol = {
            k:max(
                0.0,
                (self.xfmr_pow_dest_real[k]**2.0 +
                 self.xfmr_pow_dest_imag[k]**2.0)**0.5 -
                self.xfmr_pow_mag_max[k])
            for k in self.xfmr}

    def eval_bus_swsh_adm_imag_viol(self):

        self.bus_swsh_adm_imag_min_viol = {
            i:max(0.0, self.bus_swsh_adm_imag_min[i] - self.bus_swsh_adm_imag[i])
            for i in self.bus}
        self.bus_swsh_adm_imag_max_viol = {
            i:max(0.0, self.bus_swsh_adm_imag[i] - self.bus_swsh_adm_imag_max[i])
            for i in self.bus}

    def eval_bus_swsh_pow(self):

        self.bus_swsh_pow_imag = {
            i:(-self.bus_swsh_adm_imag[i] * self.bus_volt_mag[i]**2.0)
            for i in self.bus}

    def eval_bus_pow_balance(self):

        self.bus_pow_balance_real_viol = {
            i:abs(
                sum([self.gen_pow_real[k] for k in self.bus_gen[i] if self.gen_status[k]]) -
                sum([self.load_pow_real[k] for k in self.bus_load[i] if self.load_status[k]]) -
                sum([self.fxsh_pow_real[k] for k in self.bus_fxsh[i] if self.fxsh_status[k]]) -
                sum([self.line_pow_orig_real[k] for k in self.bus_line_orig[i] if self.line_status[k]]) -
                sum([self.line_pow_dest_real[k] for k in self.bus_line_dest[i] if self.line_status[k]]) -
                sum([self.xfmr_pow_orig_real[k] for k in self.bus_xfmr_orig[i] if self.xfmr_status[k]]) -
                sum([self.xfmr_pow_dest_real[k] for k in self.bus_xfmr_dest[i] if self.xfmr_status[k]]))
            for i in self.bus}
        self.bus_pow_balance_imag_viol = {
            i:abs(
                sum([self.gen_pow_imag[k] for k in self.bus_gen[i] if self.gen_status[k]]) -
                sum([self.load_pow_imag[k] for k in self.bus_load[i] if self.load_status[k]]) -
                sum([self.fxsh_pow_imag[k] for k in self.bus_fxsh[i] if self.fxsh_status[k]]) -
                self.bus_swsh_pow_imag[i] -
                sum([self.line_pow_orig_imag[k] for k in self.bus_line_orig[i] if self.line_status[k]]) -
                sum([self.line_pow_dest_imag[k] for k in self.bus_line_dest[i] if self.line_status[k]]) -
                sum([self.xfmr_pow_orig_imag[k] for k in self.bus_xfmr_orig[i] if self.xfmr_status[k]]) -
                sum([self.xfmr_pow_dest_imag[k] for k in self.bus_xfmr_dest[i] if self.xfmr_status[k]]))
            for i in self.bus}

    def eval_ctg_bus_volt_viol(self):

        self.ctg_bus_volt_mag_min_viol = {
            i:max(0.0, self.bus_volt_mag_min[i] - self.ctg_bus_volt_mag[i])
            for i in self.bus}
        self.ctg_bus_volt_mag_max_viol = {
            i:max(0.0, self.ctg_bus_volt_mag[i] - self.bus_volt_mag_max[i])
            for i in self.bus}

    def eval_ctg_load_pow(self):

        self.ctg_load_pow_real = {
            i:(self.load_const_pow_real[i] if self.load_status[i] else 0.0)
            for i in self.load}
        self.ctg_load_pow_imag = {
            i:(self.load_const_pow_imag[i] if self.load_status[i] else 0.0)
            for i in self.load}

    def eval_ctg_fxsh_pow(self):

        self.ctg_fxsh_pow_real = {
            i:(self.fxsh_adm_real[i] * self.ctg_bus_volt_mag[i[0]]**2.0
               if self.fxsh_status[i] else 0.0)
            for i in self.fxsh}
        self.ctg_fxsh_pow_imag = {
            i:(-self.fxsh_adm_imag[i] * self.ctg_bus_volt_mag[i[0]]**2.0
               if self.fxsh_status[i] else 0.0)
            for i in self.fxsh}

    def eval_ctg_gen_pow_real(self):

        self.ctg_gen_pow_real = {i:0.0 for i in self.gen}
        self.ctg_gen_pow_real.update(
            {i:self.gen_pow_real[i] for i in self.gen
             if self.ctg_gen_active[i]})
        self.ctg_gen_pow_real.update(
            {i:(max(self.gen_pow_real_min[i],
                    min(self.gen_pow_real_max[i],
                        self.gen_pow_real[i] +
                        self.gen_part_fact[i] *
                        self.ctg_pow_real_change)))
             for i in self.gen if self.ctg_gen_participating[i]})

    def eval_ctg_gen_pow_real_viol(self):

        self.ctg_gen_pow_real_min_viol = {
            i:max(0.0, (self.gen_pow_real_min[i] if self.ctg_gen_active[i] else 0.0) - self.ctg_gen_pow_real[i])
            for i in self.gen}
        self.ctg_gen_pow_real_max_viol = {
            i:max(0.0, self.ctg_gen_pow_real[i] - (self.gen_pow_real_max[i] if self.ctg_gen_active[i] else 0.0))
            for i in self.gen}

    def eval_ctg_gen_pow_imag_viol(self):

        self.ctg_gen_pow_imag_min_viol = {
            i:max(0.0, (self.gen_pow_imag_min[i] if self.ctg_gen_active[i] else 0.0) - self.ctg_gen_pow_imag[i])
            for i in self.gen}
        self.ctg_gen_pow_imag_max_viol = {
            i:max(0.0, self.ctg_gen_pow_imag[i] - (self.gen_pow_imag_max[i] if self.ctg_gen_active[i] else 0.0))
            for i in self.gen}

    def eval_ctg_line_pow(self):

        self.ctg_line_pow_orig_real = {
            k:( self.line_adm_real[k] * self.ctg_bus_volt_mag[k[0]]**2.0 +
                ( - self.line_adm_real[k] * math.cos(self.ctg_bus_volt_ang[k[0]] - self.ctg_bus_volt_ang[k[1]])
                  - self.line_adm_imag[k] * math.sin(self.ctg_bus_volt_ang[k[0]] - self.ctg_bus_volt_ang[k[1]])) *
                self.ctg_bus_volt_mag[k[0]] * self.ctg_bus_volt_mag[k[1]]
                if self.ctg_line_active[k] else 0.0)
            for k in self.line}
        self.ctg_line_pow_orig_imag = {
            k:( - (self.line_adm_imag[k] + 0.5 * self.line_adm_ch_imag[k]) * self.ctg_bus_volt_mag[k[0]]**2.0 +
                (   self.line_adm_imag[k] * math.cos(self.ctg_bus_volt_ang[k[0]] - self.ctg_bus_volt_ang[k[1]])
                  - self.line_adm_real[k] * math.sin(self.ctg_bus_volt_ang[k[0]] - self.ctg_bus_volt_ang[k[1]])) *
                self.ctg_bus_volt_mag[k[0]] * self.ctg_bus_volt_mag[k[1]]
                if self.ctg_line_active[k] else 0.0)
            for k in self.line}
        self.ctg_line_pow_dest_real = {
            k:( self.line_adm_real[k] * self.ctg_bus_volt_mag[k[1]]**2.0 +
                ( - self.line_adm_real[k] * math.cos(self.ctg_bus_volt_ang[k[1]] - self.ctg_bus_volt_ang[k[0]])
                  - self.line_adm_imag[k] * math.sin(self.ctg_bus_volt_ang[k[1]] - self.ctg_bus_volt_ang[k[0]])) *
                self.ctg_bus_volt_mag[k[0]] * self.ctg_bus_volt_mag[k[1]]
                if self.ctg_line_active[k] else 0.0)
            for k in self.line}
        self.ctg_line_pow_dest_imag = {
            k:( - (self.line_adm_imag[k] + 0.5 * self.line_adm_ch_imag[k]) * self.ctg_bus_volt_mag[k[1]]**2.0 +
                (   self.line_adm_imag[k] * math.cos(self.ctg_bus_volt_ang[k[1]] - self.ctg_bus_volt_ang[k[0]])
                  - self.line_adm_real[k] * math.sin(self.ctg_bus_volt_ang[k[1]] - self.ctg_bus_volt_ang[k[0]])) *
                self.ctg_bus_volt_mag[k[0]] * self.ctg_bus_volt_mag[k[1]]
                if self.ctg_line_active[k] else 0.0)
            for k in self.line}

    def eval_ctg_line_curr_viol(self):

        self.ctg_line_curr_orig_mag_max_viol = {
            k:max(
                0.0,
                (self.ctg_line_pow_orig_real[k]**2.0 +
                 self.ctg_line_pow_orig_imag[k]**2.0)**0.5 -
                self.line_curr_mag_max[k] * self.ctg_bus_volt_mag[k[0]])
            for k in self.line}
        self.ctg_line_curr_dest_mag_max_viol = {
            k:max(
                0.0,
                (self.ctg_line_pow_dest_real[k]**2.0 +
                 self.ctg_line_pow_dest_imag[k]**2.0)**0.5 -
                self.line_curr_mag_max[k] * self.ctg_bus_volt_mag[k[1]])
            for k in self.line}

    def eval_ctg_xfmr_pow(self):

        self.ctg_xfmr_pow_orig_real = {
            k:( (self.xfmr_adm_real[k] / self.xfmr_tap_mag[k]**2.0 + self.xfmr_adm_mag_real[k]) * self.ctg_bus_volt_mag[k[0]]**2.0 +
                ( - self.xfmr_adm_real[k] / self.xfmr_tap_mag[k] * math.cos(self.ctg_bus_volt_ang[k[0]] - self.ctg_bus_volt_ang[k[1]] - self.xfmr_tap_ang[k])
                  - self.xfmr_adm_imag[k] / self.xfmr_tap_mag[k] * math.sin(self.ctg_bus_volt_ang[k[0]] - self.ctg_bus_volt_ang[k[1]] - self.xfmr_tap_ang[k])) *
                self.ctg_bus_volt_mag[k[0]] * self.ctg_bus_volt_mag[k[1]]
                if self.ctg_xfmr_active[k] else 0.0)
            for k in self.xfmr}
        self.ctg_xfmr_pow_orig_imag = {
            k:( - (self.xfmr_adm_imag[k] / self.xfmr_tap_mag[k]**2.0 + self.xfmr_adm_mag_imag[k]) * self.ctg_bus_volt_mag[k[0]]**2.0 +
                (   self.xfmr_adm_imag[k] / self.xfmr_tap_mag[k] * math.cos(self.ctg_bus_volt_ang[k[0]] - self.ctg_bus_volt_ang[k[1]] - self.xfmr_tap_ang[k])
                    - self.xfmr_adm_real[k] / self.xfmr_tap_mag[k] * math.sin(self.ctg_bus_volt_ang[k[0]] - self.ctg_bus_volt_ang[k[1]] - self.xfmr_tap_ang[k])) *
                self.ctg_bus_volt_mag[k[0]] * self.ctg_bus_volt_mag[k[1]]
                if self.ctg_xfmr_active[k] else 0.0)
            for k in self.xfmr}
        self.ctg_xfmr_pow_dest_real = {
            k:( self.xfmr_adm_real[k] * self.ctg_bus_volt_mag[k[1]]**2.0 +
                ( - self.xfmr_adm_real[k] / self.xfmr_tap_mag[k] * math.cos(self.ctg_bus_volt_ang[k[1]] - self.ctg_bus_volt_ang[k[0]] + self.xfmr_tap_ang[k])
                  - self.xfmr_adm_imag[k] / self.xfmr_tap_mag[k] * math.sin(self.ctg_bus_volt_ang[k[1]] - self.ctg_bus_volt_ang[k[0]] + self.xfmr_tap_ang[k])) *
                self.ctg_bus_volt_mag[k[0]] * self.ctg_bus_volt_mag[k[1]]
                if self.ctg_xfmr_active[k] else 0.0)
            for k in self.xfmr}
        self.ctg_xfmr_pow_dest_imag = {
            k:( - self.xfmr_adm_imag[k] * self.ctg_bus_volt_mag[k[1]]**2.0 +
                (   self.xfmr_adm_imag[k] / self.xfmr_tap_mag[k] * math.cos(self.ctg_bus_volt_ang[k[1]] - self.ctg_bus_volt_ang[k[0]] + self.xfmr_tap_ang[k])
                    - self.xfmr_adm_real[k] / self.xfmr_tap_mag[k] * math.sin(self.ctg_bus_volt_ang[k[1]] - self.ctg_bus_volt_ang[k[0]] + self.xfmr_tap_ang[k])) *
                self.ctg_bus_volt_mag[k[0]] * self.ctg_bus_volt_mag[k[1]]
                if self.ctg_xfmr_active[k] else 0.0)
            for k in self.xfmr}

    def eval_ctg_xfmr_pow_viol(self):

        self.ctg_xfmr_pow_orig_mag_max_viol = {
            k:max(
                0.0,
                (self.ctg_xfmr_pow_orig_real[k]**2.0 +
                 self.ctg_xfmr_pow_orig_imag[k]**2.0)**0.5 -
                self.xfmr_pow_mag_max[k])
            for k in self.xfmr}
        self.ctg_xfmr_pow_dest_mag_max_viol = {
            k:max(
                0.0,
                (self.ctg_xfmr_pow_dest_real[k]**2.0 +
                 self.ctg_xfmr_pow_dest_imag[k]**2.0)**0.5 -
                self.xfmr_pow_mag_max[k])
            for k in self.xfmr}

    def eval_ctg_bus_swsh_adm_imag_viol(self):

        self.ctg_bus_swsh_adm_imag_max_viol = {
            i:max(0.0, self.ctg_bus_swsh_adm_imag[i] - self.bus_swsh_adm_imag_max[i])
            for i in self.bus}
        self.ctg_bus_swsh_adm_imag_min_viol = {
            i:max(0.0, self.bus_swsh_adm_imag_min[i] - self.ctg_bus_swsh_adm_imag[i])
            for i in self.bus}

    def eval_ctg_bus_swsh_pow(self):

        self.ctg_bus_swsh_pow_imag = {
            i:(-self.ctg_bus_swsh_adm_imag[i] * self.ctg_bus_volt_mag[i]**2.0)
            for i in self.bus}

    def eval_ctg_bus_pow_balance(self):

        self.ctg_bus_pow_balance_real_viol = {
            i:abs(
                sum([self.ctg_gen_pow_real[k] for k in self.bus_gen[i] if self.ctg_gen_active[k]]) -
                sum([self.ctg_load_pow_real[k] for k in self.bus_load[i] if self.load_status[k]]) -
                sum([self.ctg_fxsh_pow_real[k] for k in self.bus_fxsh[i] if self.fxsh_status[k]]) -
                sum([self.ctg_line_pow_orig_real[k] for k in self.bus_line_orig[i] if self.ctg_line_active[k]]) -
                sum([self.ctg_line_pow_dest_real[k] for k in self.bus_line_dest[i] if self.ctg_line_active[k]]) -
                sum([self.ctg_xfmr_pow_orig_real[k] for k in self.bus_xfmr_orig[i] if self.ctg_xfmr_active[k]]) -
                sum([self.ctg_xfmr_pow_dest_real[k] for k in self.bus_xfmr_dest[i] if self.ctg_xfmr_active[k]]))
            for i in self.bus}
        self.ctg_bus_pow_balance_imag_viol = {
            i:abs(
                sum([self.ctg_gen_pow_imag[k] for k in self.bus_gen[i] if self.ctg_gen_active[k]]) -
                sum([self.ctg_load_pow_imag[k] for k in self.bus_load[i] if self.load_status[k]]) -
                sum([self.ctg_fxsh_pow_imag[k] for k in self.bus_fxsh[i] if self.fxsh_status[k]]) -
                self.ctg_bus_swsh_pow_imag[i] -
                sum([self.ctg_line_pow_orig_imag[k] for k in self.bus_line_orig[i] if self.ctg_line_active[k]]) -
                sum([self.ctg_line_pow_dest_imag[k] for k in self.bus_line_dest[i] if self.ctg_line_active[k]]) -
                sum([self.ctg_xfmr_pow_orig_imag[k] for k in self.bus_xfmr_orig[i] if self.ctg_xfmr_active[k]]) -
                sum([self.ctg_xfmr_pow_dest_imag[k] for k in self.bus_xfmr_dest[i] if self.ctg_xfmr_active[k]]))
            for i in self.bus}

    def eval_ctg_gen_pvpq_viol(self):

        self.ctg_gen_pvpq1_viol = {
            i:(min(max(0.0, self.gen_pow_imag_max[i] - self.ctg_gen_pow_imag[i]),
                   max(0.0, self.bus_volt_mag[i[0]] - self.ctg_bus_volt_mag[i[0]]))
                if self.ctg_gen_active[i]
                else 0.0)
            for i in self.gen}
        self.ctg_gen_pvpq2_viol = {
            i:(min(max(0.0, self.ctg_gen_pow_imag[i] - self.gen_pow_imag_min[i]),
                   max(0.0, self.ctg_bus_volt_mag[i[0]] - self.bus_volt_mag[i[0]]))
                if self.ctg_gen_active[i]
                else 0.0)
            for i in self.gen}

    def eval_penalty(self):

        self.penalty = self.pow_pen * (
            sum(self.line_curr_orig_mag_max_viol.values()) +
            sum(self.line_curr_dest_mag_max_viol.values()) +
            sum(self.xfmr_pow_orig_mag_max_viol.values()) +
            sum(self.xfmr_pow_dest_mag_max_viol.values()) +
            sum(self.bus_pow_balance_real_viol.values()) +
            sum(self.bus_pow_balance_imag_viol.values()))

    def eval_ctg_penalty(self):

        self.ctg_penalty = self.pow_pen * (
            sum(self.ctg_line_curr_orig_mag_max_viol.values()) +
            sum(self.ctg_line_curr_dest_mag_max_viol.values()) +
            sum(self.ctg_xfmr_pow_orig_mag_max_viol.values()) +
            sum(self.ctg_xfmr_pow_dest_mag_max_viol.values()) +
            sum(self.ctg_bus_pow_balance_real_viol.values()) +
            sum(self.ctg_bus_pow_balance_imag_viol.values()))

    def eval_infeas(self):

        self.infeas = (
            1 if (
                self.max_bus_volt_mag_max_viol[1] > 0.0 or
                self.max_bus_volt_mag_min_viol[1] > 0.0 or
                self.max_bus_swsh_adm_imag_max_viol[1] > 0.0 or
                self.max_bus_swsh_adm_imag_min_viol[1] > 0.0 or
                self.max_gen_pow_real_max_viol[1] > 0.0 or
                self.max_gen_pow_real_min_viol[1] > 0.0 or
                self.max_gen_pow_imag_max_viol[1] > 0.0 or
                self.max_gen_pow_imag_min_viol[1] > 0.0 or
                self.max_line_curr_orig_mag_max_viol[1] > 0.0 or
                self.max_line_curr_dest_mag_max_viol[1] > 0.0 or
                self.max_xfmr_pow_orig_mag_max_viol[1] > 0.0 or
                self.max_xfmr_pow_dest_mag_max_viol[1] > 0.0)
            else 0)

    def eval_ctg_infeas(self):

        self.ctg_infeas = (
            1 if (
                self.ctg_max_bus_volt_mag_max_viol[1] > 0.0 or
                self.ctg_max_bus_volt_mag_min_viol[1] > 0.0 or
                self.ctg_max_bus_swsh_adm_imag_max_viol[1] > 0.0 or
                self.ctg_max_bus_swsh_adm_imag_min_viol[1] > 0.0 or
                self.ctg_max_gen_pow_real_max_viol[1] > 0.0 or
                self.ctg_max_gen_pow_real_min_viol[1] > 0.0 or
                self.ctg_max_gen_pow_imag_max_viol[1] > 0.0 or
                self.ctg_max_gen_pow_imag_min_viol[1] > 0.0 or
                self.ctg_max_gen_pvpq1_viol[1] > 0.0 or
                self.ctg_max_gen_pvpq2_viol[1] > 0.0 or
                self.ctg_max_line_curr_orig_mag_max_viol[1] > 0.0 or
                self.ctg_max_line_curr_dest_mag_max_viol[1] > 0.0 or
                self.ctg_max_xfmr_pow_orig_mag_max_viol[1] > 0.0 or
                self.ctg_max_xfmr_pow_dest_mag_max_viol[1] > 0.0)
            else 0)

    def eval_obj(self):

        self.obj = self.cost + self.penalty

    #def evaluate(self):
    #
    #    # obj
    #    self.eval_cost()
    #    self.eval_penalty()
    #    self.eval_obj()

    def normalize(self):
        '''divide constraint violations by a normalizing constant.'''

        pass

    # TODO convert back from per unit to data units here for printing to detail and summary output files
    # should we use data units for the output of the function? Yes
    def convert_to_data_units(self):
        '''convert from computation units (p.u.) to data units (mix of p.u. and phycical units)
        for writing output'''

        pass

    def compute_detail(self):

        def extra_max(d):
            if len(d) == 0:
                return (None, 0.0)
            else:
                k = max(d.keys(), key=(lambda k: d[k]))
                return (k, d[k])
        
        self.max_bus_volt_mag_max_viol = extra_max(self.bus_volt_mag_max_viol)
        self.max_bus_volt_mag_min_viol = extra_max(self.bus_volt_mag_min_viol)
        self.max_bus_swsh_adm_imag_max_viol = extra_max(self.bus_swsh_adm_imag_max_viol)
        self.max_bus_swsh_adm_imag_min_viol = extra_max(self.bus_swsh_adm_imag_min_viol)
        self.max_bus_pow_balance_real_viol = extra_max(self.bus_pow_balance_real_viol)
        self.max_bus_pow_balance_imag_viol = extra_max(self.bus_pow_balance_imag_viol)
        self.max_gen_pow_real_max_viol = extra_max(self.gen_pow_real_max_viol)
        self.max_gen_pow_real_min_viol = extra_max(self.gen_pow_real_min_viol)
        self.max_gen_pow_imag_max_viol = extra_max(self.gen_pow_imag_max_viol)
        self.max_gen_pow_imag_min_viol = extra_max(self.gen_pow_imag_min_viol)
        self.max_line_curr_orig_mag_max_viol = extra_max(self.line_curr_orig_mag_max_viol)
        self.max_line_curr_dest_mag_max_viol = extra_max(self.line_curr_dest_mag_max_viol)
        self.max_xfmr_pow_orig_mag_max_viol = extra_max(self.xfmr_pow_orig_mag_max_viol)
        self.max_xfmr_pow_dest_mag_max_viol = extra_max(self.xfmr_pow_dest_mag_max_viol)

    def compute_ctg_detail(self):

        def extra_max(d):
            if len(d) == 0:
                return (None, 0.0)
            else:
                k = max(d.keys(), key=(lambda k: d[k]))
                return (k, d[k])
        
        self.ctg_max_bus_volt_mag_max_viol = extra_max(self.ctg_bus_volt_mag_max_viol)
        self.ctg_max_bus_volt_mag_min_viol = extra_max(self.ctg_bus_volt_mag_min_viol)
        self.ctg_max_bus_swsh_adm_imag_max_viol = extra_max(self.ctg_bus_swsh_adm_imag_max_viol)
        self.ctg_max_bus_swsh_adm_imag_min_viol = extra_max(self.ctg_bus_swsh_adm_imag_min_viol)
        self.ctg_max_bus_pow_balance_real_viol = extra_max(self.ctg_bus_pow_balance_real_viol)
        self.ctg_max_bus_pow_balance_imag_viol = extra_max(self.ctg_bus_pow_balance_imag_viol)
        self.ctg_max_gen_pow_real_max_viol = extra_max(self.ctg_gen_pow_real_max_viol)
        self.ctg_max_gen_pow_real_min_viol = extra_max(self.ctg_gen_pow_real_min_viol)
        self.ctg_max_gen_pow_imag_max_viol = extra_max(self.ctg_gen_pow_imag_max_viol)
        self.ctg_max_gen_pow_imag_min_viol = extra_max(self.ctg_gen_pow_imag_min_viol)
        self.ctg_max_gen_pvpq1_viol = extra_max(self.ctg_gen_pvpq1_viol)
        self.ctg_max_gen_pvpq2_viol = extra_max(self.ctg_gen_pvpq2_viol)
        self.ctg_max_line_curr_orig_mag_max_viol = extra_max(self.ctg_line_curr_orig_mag_max_viol)
        self.ctg_max_line_curr_dest_mag_max_viol = extra_max(self.ctg_line_curr_dest_mag_max_viol)
        self.ctg_max_xfmr_pow_orig_mag_max_viol = extra_max(self.ctg_xfmr_pow_orig_mag_max_viol)
        self.ctg_max_xfmr_pow_dest_mag_max_viol = extra_max(self.ctg_xfmr_pow_dest_mag_max_viol)

    def compute_summary(self):

        def dict_max_zero(d):
            return max([0] + d.values())

        self.max_bus_volt_mag_min_viol = dict_max_zero(self.bus_volt_mag_min_viol)
        self.max_bus_volt_mag_max_viol = dict_max_zero(self.bus_volt_mag_max_viol)
        self.max_gen_pow_real_min_viol = dict_max_zero(self.gen_pow_real_min_viol)
        self.max_gen_pow_real_max_viol = dict_max_zero(self.gen_pow_real_max_viol)
        self.max_gen_pow_imag_min_viol = dict_max_zero(self.gen_pow_imag_min_viol)
        self.max_gen_pow_imag_max_viol = dict_max_zero(self.gen_pow_imag_max_viol)
        self.max_line_curr_orig_mag_max_viol = dict_max_zero(self.line_curr_orig_mag_max_viol)
        self.max_line_curr_dest_mag_max_viol = dict_max_zero(self.line_curr_dest_mag_max_viol)
        self.max_xfmr_pow_orig_mag_max_viol = dict_max_zero(self.xfmr_pow_orig_mag_max_viol)
        self.max_xfmr_pow_dest_mag_max_viol = dict_max_zero(self.xfmr_pow_dest_mag_max_viol)
        self.max_swsh_adm_imag_min_viol = dict_max_zero(self.swsh_adm_imag_min_viol)
        self.max_swsh_adm_imag_max_viol = dict_max_zero(self.swsh_adm_imag_max_viol)
        self.max_bus_pow_balance_real_viol = dict_max_zero(self.bus_pow_balance_real_viol)
        self.max_bus_pow_balance_imag_viol = dict_max_zero(self.bus_pow_balance_imag_viol)
        self.max_bus_ctg_volt_mag_max_viol = dict_max_zero(self.bus_ctg_volt_mag_max_viol)
        self.max_bus_ctg_volt_mag_min_viol = dict_max_zero(self.bus_ctg_volt_mag_min_viol)
        self.max_gen_ctg_pow_real_min_viol = dict_max_zero(self.gen_ctg_pow_real_min_viol)
        self.max_gen_ctg_pow_real_max_viol = dict_max_zero(self.gen_ctg_pow_real_max_viol)
        self.max_gen_ctg_pow_imag_min_viol = dict_max_zero(self.gen_ctg_pow_imag_min_viol)
        self.max_gen_ctg_pow_imag_max_viol = dict_max_zero(self.gen_ctg_pow_imag_max_viol)
        self.max_line_ctg_curr_orig_mag_max_viol = dict_max_zero(self.line_ctg_curr_orig_mag_max_viol)
        self.max_line_ctg_curr_dest_mag_max_viol = dict_max_zero(self.line_ctg_curr_dest_mag_max_viol)
        self.max_xfmr_ctg_pow_orig_mag_max_viol = dict_max_zero(self.xfmr_ctg_pow_orig_mag_max_viol)
        self.max_xfmr_ctg_pow_dest_mag_max_viol = dict_max_zero(self.xfmr_ctg_pow_dest_mag_max_viol)
        self.max_swsh_ctg_adm_imag_min_viol = dict_max_zero(self.swsh_ctg_adm_imag_min_viol)
        self.max_swsh_ctg_adm_imag_max_viol = dict_max_zero(self.swsh_ctg_adm_imag_max_viol)
        self.max_bus_ctg_pow_balance_real_viol = dict_max_zero(self.bus_ctg_pow_balance_real_viol)
        self.max_bus_ctg_pow_balance_imag_viol = dict_max_zero(self.bus_ctg_pow_balance_imag_viol)
        # todo: complementarity violation on generator bus voltage and generator reactive power
        self.max_gen_ctg_pvpq1_viol = dict_max_zero(self.gen_ctg_pvpq1_viol)
        self.max_gen_ctg_pvpq2_viol = dict_max_zero(self.gen_ctg_pvpq2_viol)

        self.max_viol = max(
            self.max_bus_volt_mag_min_viol,
            self.max_bus_volt_mag_max_viol,
            self.max_gen_pow_real_min_viol,
            self.max_gen_pow_real_max_viol,
            self.max_gen_pow_imag_min_viol,
            self.max_gen_pow_imag_max_viol,
            self.max_line_curr_orig_mag_max_viol,
            self.max_line_curr_dest_mag_max_viol,
            self.max_xfmr_pow_orig_mag_max_viol,
            self.max_xfmr_pow_dest_mag_max_viol,
            self.max_swsh_adm_imag_min_viol,
            self.max_swsh_adm_imag_max_viol,
            self.max_bus_pow_balance_real_viol,
            self.max_bus_pow_balance_imag_viol,
            self.max_bus_ctg_volt_mag_max_viol,
            self.max_bus_ctg_volt_mag_min_viol,
            self.max_gen_ctg_pow_imag_min_viol,
            self.max_gen_ctg_pow_imag_max_viol,
            self.max_gen_ctg_pow_real_min_viol,
            self.max_gen_ctg_pow_real_max_viol,
            self.max_line_ctg_curr_orig_mag_max_viol,
            self.max_line_ctg_curr_dest_mag_max_viol,
            self.max_xfmr_ctg_pow_orig_mag_max_viol,
            self.max_xfmr_ctg_pow_dest_mag_max_viol,
            self.max_swsh_ctg_adm_imag_min_viol,
            self.max_swsh_ctg_adm_imag_max_viol,
            self.max_bus_ctg_pow_balance_real_viol,
            self.max_bus_ctg_pow_balance_imag_viol,
            self.max_gen_ctg_pvpq1_viol,
            self.max_gen_ctg_pvpq2_viol,
        )

        self.max_nonobj_viol = 0.0 # todo need to actually compute this, but so far there are no nonobjective constraints to violate anyway
        self.num_viol = 0


    def write_summary(self, out_name):

        with open(out_name, 'ab') as out:
            csv_writer = csv.writer(out, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
        
            if self.scenario_number == '1':
                
                csv_writer.writerow([
                '','','','','',
                'Maximum base case constraint violations','','','','','','','','','','','','','',
                'Maximum contingency case constraint violations'
                ])
                
                csv_writer.writerow([
                'Scenario',
                'Objective',
                'Cost',
                'Objective-Cost',
                'Runtime(sec)',
                'bus_volt_mag_min',
                'bus_volt_mag_max',
                'gen_pow_real_min',
                'gen_pow_real_max',
                'gen_pow_imag_min',
                'gen_pow_imag_max',
                'line_curr_orig_mag_max',
                'line_curr_dest_mag_max',
                'xfmr_pow_orig_mag_max',
                'xfrm_pow_dest_mag_max',
                'swsh_adm_imag_min',
                'swsh_adm_imag_max',
                'bus_pow_balance_real',
                'bus_pow_balance_imag',
                'bus_ctg_volt_mag_min',
                'bus_ctg_volt_mag_max',
                'gen_ctg_pow_real_min',
                'gen_ctg_pow_real_max',
                'gen_ctg_pow_imag_min',
                'gen_ctg_pow_imag_max',
                'line_ctg_curr_orig_mag_max',
                'line_ctg_curr_dest_mag_max',
                'xfmr_ctg_pow_orig_mag_max',
                'xfmr_ctg_pow_dest_mag_max',
                'swsh_ctg_adm_imag_min',
                'swsh_ctg_adm_imag_max',
                'bus_ctg_pow_balance_real',
                'bus_ctg_pow_balance_imag',
                'gen_ctg_pvpq1',
                'gen_ctg_pvpq2',
                'all'])

            csv_writer.writerow([
                'scenario_%s'%(self.scenario_number),
                self.obj,
                self.cost,
                self.obj-self.cost,
                self.runtime_sec,
                self.max_bus_volt_mag_min_viol,
                self.max_bus_volt_mag_max_viol,
                self.max_gen_pow_real_min_viol,
                self.max_gen_pow_real_max_viol,
                self.max_gen_pow_imag_min_viol,
                self.max_gen_pow_imag_max_viol,
                self.max_line_curr_orig_mag_max_viol,
                self.max_line_curr_dest_mag_max_viol,
                self.max_xfmr_pow_orig_mag_max_viol,
                self.max_xfmr_pow_dest_mag_max_viol,
                self.max_swsh_adm_imag_min_viol,
                self.max_swsh_adm_imag_max_viol,
                self.max_bus_pow_balance_real_viol,
                self.max_bus_pow_balance_imag_viol,
                self.max_bus_ctg_volt_mag_min_viol,
                self.max_bus_ctg_volt_mag_max_viol,
                self.max_gen_ctg_pow_real_min_viol,
                self.max_gen_ctg_pow_real_max_viol,
                self.max_gen_ctg_pow_imag_min_viol,
                self.max_gen_ctg_pow_imag_max_viol,
                self.max_line_ctg_curr_orig_mag_max_viol,
                self.max_line_ctg_curr_dest_mag_max_viol,
                self.max_xfmr_ctg_pow_orig_mag_max_viol,
                self.max_xfmr_ctg_pow_dest_mag_max_viol,
                self.max_swsh_ctg_adm_imag_min_viol,
                self.max_swsh_ctg_adm_imag_max_viol,
                self.max_bus_ctg_pow_balance_real_viol,
                self.max_bus_ctg_pow_balance_imag_viol,
                self.max_gen_ctg_pvpq1_viol,
                self.max_gen_ctg_pvpq2_viol,
                self.max_viol])
        

    def get_top_violations(self, top_keys, items):
        top_i=0
        for key, value in sorted(items, key=lambda (k,v): (v,k), reverse=True):
            top_keys[key]=True
            top_i += 1
            if top_i >= TOP_N:
                break

    def write_bus_contingencies(self, csv_writer):
        csv_writer.writerow(['--bus ctg'])
        csv_writer.writerow([
            'bus_i', 'ctg', 'bus_ctg_volt_mag_min_viol', 'bus_ctg_volt_mag_max_viol',
            'bus_ctg_pow_balance_real_viol', 'bus_ctg_pow_balance_imag_viol'])

        start_time = time.time()
        if TOP_N > 0:
            top_keys = OrderedDict()
            self.get_top_violations(top_keys, self.bus_ctg_pow_balance_real_viol.iteritems())    
            self.get_top_violations(top_keys, self.bus_ctg_pow_balance_imag_viol.iteritems())
    
            for key in top_keys:   
                csv_writer.writerow([key[0], key[1], self.bus_ctg_volt_mag_min_viol[key], self.bus_ctg_volt_mag_max_viol[key],self.bus_ctg_pow_balance_real_viol[key], self.bus_ctg_pow_balance_imag_viol[key]])
        else:   
            # timing some different write methods
            # number 1 is still the fastest oddly
            for i in self.bus:
                for k in self.ctg:
                    csv_writer.writerow([
                        i, k, self.bus_ctg_volt_mag_min_viol[(i,k)], self.bus_ctg_volt_mag_max_viol[(i,k)],
                        self.bus_ctg_pow_balance_real_viol[(i,k)], self.bus_ctg_pow_balance_imag_viol[(i,k)]])
        time_elapsed = time.time() - start_time
        print 'write bus ctg time (1): %u' % time_elapsed

    def write_line_contingencies(self, csv_writer):
        csv_writer.writerow(['--line ctg'])
        csv_writer.writerow([
            'line_i', 'line_j', 'line_id', 'ctg', 'line_ctg_curr_orig_mag_max_viol',
            'line_ctg_curr_dest_mag_max_viol'])

        start_time = time.time()
        if TOP_N > 0:
            top_keys = OrderedDict()    
            self.get_top_violations(top_keys, self.line_ctg_curr_orig_mag_max_viol.iteritems())
            self.get_top_violations(top_keys, self.line_ctg_curr_dest_mag_max_viol.iteritems())
            
            for key in top_keys:   
                csv_writer.writerow([
                    key[0], key[1], key[2], key[3], self.line_ctg_curr_orig_mag_max_viol[(key[0],key[1],key[2],key[3])],
                    self.line_ctg_curr_dest_mag_max_viol[(key[0],key[1],key[2],key[3])]])
        else:   
            for i in self.line:
                for k in self.ctg:
                    csv_writer.writerow([
                        i[0], i[1], i[2], k, self.line_ctg_curr_orig_mag_max_viol[(i[0],i[1],i[2],k)],
                        self.line_ctg_curr_dest_mag_max_viol[(i[0],i[1],i[2],k)]])
        time_elapsed = time.time() - start_time
        print 'write line ctg time (1): %u' % time_elapsed
        
        
    def write_gen_contingencies(self, csv_writer):
        csv_writer.writerow(['--gen ctg'])
        csv_writer.writerow([
            'gen_i', 'gen_id', 'ctg', 'gen_ctg_pow_real_min_viol', 'gen_ctg_pow_real_max_viol',
            'gen_ctg_pow_imag_min_viol', 'gen_ctg_pow_imag_max_viol', 'gen_ctg_pvpq1_viol', 'gen_ctg_pvpq2_viol'])
        
        if TOP_N > 0:
            top_keys = OrderedDict()    
            self.get_top_violations(top_keys, self.gen_ctg_pow_real_min_viol.iteritems())
            self.get_top_violations(top_keys, self.gen_ctg_pow_real_max_viol.iteritems())
            self.get_top_violations(top_keys, self.gen_ctg_pow_imag_min_viol.iteritems())
            self.get_top_violations(top_keys, self.gen_ctg_pow_imag_max_viol.iteritems())
            self.get_top_violations(top_keys, self.gen_ctg_pvpq2_viol.iteritems())
            self.get_top_violations(top_keys, self.gen_ctg_pvpq1_viol.iteritems())
            
            for key in top_keys:   
                csv_writer.writerow([
                    key[0], key[1], key[2], 
                    self.gen_ctg_pow_real_min_viol[(key[0],key[1],key[2])],
                    self.gen_ctg_pow_real_max_viol[(key[0],key[1],key[2])],
                    self.gen_ctg_pow_imag_min_viol[(key[0],key[1],key[2])],
                    self.gen_ctg_pow_imag_max_viol[(key[0],key[1],key[2])],
                    self.gen_ctg_pvpq2_viol[(key[0],key[1],key[2])],
                    self.gen_ctg_pvpq1_viol[(key[0],key[1],key[2])]])
        else:        
            for i in self.gen:
                for k in self.ctg:
                    csv_writer.writerow([
                        i[0], i[1], k, self.gen_ctg_pow_real_min_viol[(i[0],i[1],k)],
                        self.gen_ctg_pow_real_max_viol[(i[0],i[1],k)],
                        self.gen_ctg_pow_imag_min_viol[(i[0],i[1],k)],
                        self.gen_ctg_pow_imag_max_viol[(i[0],i[1],k)],
                        self.gen_ctg_pvpq2_viol[(i[0],i[1],k)],
                        self.gen_ctg_pvpq1_viol[(i[0],i[1],k)]])
           
    def write_transformer_contingencies(self, csv_writer):
        csv_writer.writerow(['--xfmr ctg'])
        csv_writer.writerow([
            'xfmr_i', 'xfmr_j', 'xfmr_id', 'ctg', 'xfmr_ctg_pow_orig_mag_max_viol',
            'xfmr_ctg_pow_dest_mag_max_viol'])
        
        if TOP_N > 0:
            top_keys = OrderedDict()    
            self.get_top_violations(top_keys, self.xfmr_ctg_pow_orig_mag_max_viol.iteritems())
            self.get_top_violations(top_keys, self.xfmr_ctg_pow_dest_mag_max_viol.iteritems())
            
            for key in top_keys:   
                csv_writer.writerow([
                    key[0], key[1], key[2], key[3],
                    self.xfmr_ctg_pow_orig_mag_max_viol[(key[0],key[1],key[2], key[3])],
                    self.xfmr_ctg_pow_dest_mag_max_viol[(key[0],key[1],key[2], key[3])]
                    ])
        else:    
            for i in self.xfmr:
                for k in self.ctg:
                    csv_writer.writerow([
                        i[0], i[1], i[2], k, 
                        self.xfmr_ctg_pow_orig_mag_max_viol[(i[0],i[1],i[2],k)],
                        self.xfmr_ctg_pow_dest_mag_max_viol[(i[0],i[1],i[2],k)]])

    def write_swsh_contingencies(self, csv_writer):
        csv_writer.writerow(['--swsh ctg'])
        csv_writer.writerow([
            'swsh_i', 'ctg', 'swsh_ctg_adm_imag_min_viol', 'swsh_ctg_adm_imag_max_viol'])
        
        if TOP_N > 0:
            top_keys = OrderedDict()
            self.get_top_violations(top_keys, self.swsh_ctg_adm_imag_min_viol.iteritems())
            self.get_top_violations(top_keys, self.swsh_ctg_adm_imag_max_viol.iteritems())
            
            for key in top_keys:   
                csv_writer.writerow([
                    key[0], key[1],
                    self.swsh_ctg_adm_imag_min_viol[(key[0],key[1])],
                    self.swsh_ctg_adm_imag_max_viol[(key[0],key[1])]
                    ])
        else:    
            for i in self.swsh:
                for k in self.ctg:
                    csv_writer.writerow([
                        i, k, 
                        self.swsh_ctg_adm_imag_min_viol[(i,k)],
                        self.swsh_ctg_adm_imag_max_viol[(i,k)]])
                
           
    def write_bus_base_violations(self, csv_writer):
        csv_writer.writerow(['--bus'])
        csv_writer.writerow([
            'bus_i', 'bus_volt_mag_min_viol', 'bus_volt_mag_max_viol',
            'bus_pow_balance_real_viol', 'bus_pow_balance_imag_viol'])
        
        if TOP_N > 0:
            top_keys = OrderedDict()   
            self.get_top_violations(top_keys, self.bus_volt_mag_min_viol.iteritems())    
            self.get_top_violations(top_keys, self.bus_volt_mag_max_viol.iteritems())
            self.get_top_violations(top_keys, self.bus_pow_balance_real_viol.iteritems())
            self.get_top_violations(top_keys, self.bus_pow_balance_imag_viol.iteritems())
    
            for key in top_keys:   
                csv_writer.writerow([key, self.bus_volt_mag_min_viol[key], self.bus_volt_mag_max_viol[key],self.bus_pow_balance_real_viol[key], self.bus_pow_balance_imag_viol[key]])
 
        else:
            for i in self.bus:
                csv_writer.writerow([
                    i, self.bus_volt_mag_min_viol[i], self.bus_volt_mag_max_viol[i],
                    self.bus_pow_balance_real_viol[i], self.bus_pow_balance_imag_viol[i]])
                    
    def write_gen_base_violations(self, csv_writer):
        csv_writer.writerow(['--gen'])
        csv_writer.writerow([
            'gen_i', 'gen_id', 'gen_pow_real_min_viol', 'gen_pow_real_max_viol',
            'gen_pow_imag_min_viol', 'gen_pow_imag_max_viol'])
        
        if TOP_N > 0:
            top_keys = OrderedDict()    
            self.get_top_violations(top_keys, self.gen_pow_real_min_viol.iteritems())
            self.get_top_violations(top_keys, self.gen_pow_real_max_viol.iteritems())
            self.get_top_violations(top_keys, self.gen_pow_imag_min_viol.iteritems())
            self.get_top_violations(top_keys, self.gen_pow_imag_max_viol.iteritems())
            
            for key in top_keys:   
                csv_writer.writerow([
                    key[0], key[1], 
                    self.gen_pow_real_min_viol[(key[0],key[1])],
                    self.gen_pow_real_max_viol[(key[0],key[1])],
                    self.gen_pow_imag_min_viol[(key[0],key[1])],
                    self.gen_pow_imag_max_viol[(key[0],key[1])]])
        else:
            for i in self.gen:
                csv_writer.writerow([
                    i[0], i[1], self.gen_pow_real_min_viol[i], self.gen_pow_real_max_viol[i],
                    self.gen_pow_imag_min_viol[i], self.gen_pow_imag_max_viol[i]])
     
    def write_line_base_violations(self, csv_writer):
        csv_writer.writerow(['--line'])
        csv_writer.writerow([
            'line_i', 'line_j', 'line_id', 'line_curr_orig_mag_max_viol',
            'line_curr_dest_mag_max_viol'])
         
        if TOP_N > 0:
            top_keys = OrderedDict()    
            self.get_top_violations(top_keys, self.line_curr_orig_mag_max_viol.iteritems())
            self.get_top_violations(top_keys, self.line_curr_dest_mag_max_viol.iteritems())
            
            for key in top_keys:   
                csv_writer.writerow([
                    key[0], key[1], key[2], 
                    self.line_curr_orig_mag_max_viol[(key[0],key[1],key[2])],
                    self.line_curr_dest_mag_max_viol[(key[0],key[1],key[2])]])
        else:
            for i in self.line:
                csv_writer.writerow([
                    i[0], i[1], i[2], 
                    self.line_curr_orig_mag_max_viol[i],
                    self.line_curr_dest_mag_max_viol[i]])
       
    def write_transformer_base_violations(self, csv_writer):
        csv_writer.writerow(['--xfmr'])
        csv_writer.writerow([
                'xfmr_i', 'xfmr_j', 'xfmr_id', 'xfmr_pow_orig_mag_max_viol',
                'xfmr_pow_dest_mag_max_viol'])
            
        if TOP_N > 0:
            top_keys = OrderedDict()    
            self.get_top_violations(top_keys, self.xfmr_pow_orig_mag_max_viol.iteritems())
            self.get_top_violations(top_keys, self.xfmr_pow_dest_mag_max_viol.iteritems())
            
            for key in top_keys:   
                csv_writer.writerow([
                    key[0], key[1], key[2],
                    self.xfmr_pow_dest_mag_max_viol[key],
                    self.xfmr_pow_dest_mag_max_viol[key]
                    ])
        else:
            for i in self.xfmr:
                csv_writer.writerow([
                    i[0], i[1], i[2], 
                    self.xfmr_pow_orig_mag_max_viol[i],
                    self.xfmr_pow_dest_mag_max_viol[i]])

    def write_swsh_base_violations(self, csv_writer):
        csv_writer.writerow(['--swsh'])
        csv_writer.writerow([
            'swsh_i', 'swsh_adm_imag_min_viol', 'swsh_adm_imag_max_viol'])
        
        if TOP_N > 0:
            top_keys = OrderedDict()
            self.get_top_violations(top_keys, self.swsh_adm_imag_min_viol.iteritems())
            self.get_top_violations(top_keys, self.swsh_adm_imag_max_viol.iteritems())
            
            for key in top_keys:   
                csv_writer.writerow([
                    key,
                    self.swsh_adm_imag_min_viol[key],
                    self.swsh_adm_imag_max_viol[key]
                    ])
        else:
            for i in self.swsh:
                csv_writer.writerow([
                    i, self.swsh_adm_imag_min_viol[i], self.swsh_adm_imag_max_viol[i]])
                

    def write_detail(self, out_name):
        
        with open(out_name, 'wb') as out:
            csv_writer = csv.writer(out, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['evaluation detail'])
            csv_writer.writerow(['--summary'])
            csv_writer.writerow(['obj', 'cost', 'penalty', 'max_nonobj_viol', 'max_viol'])
            csv_writer.writerow([self.obj, self.cost, self.penalty, self.max_nonobj_viol, self.max_viol])
            csv_writer.writerow(['--constr viol summary'])
            csv_writer.writerow(['constr_type', 'max_viol'])
            csv_writer.writerow(['bus_volt_mag_min', self.max_bus_volt_mag_min_viol])
            csv_writer.writerow(['bus_volt_mag_max', self.max_bus_volt_mag_max_viol])
            csv_writer.writerow(['gen_pow_real_min', self.max_gen_pow_real_min_viol])
            csv_writer.writerow(['gen_pow_real_max', self.max_gen_pow_real_max_viol])
            csv_writer.writerow(['gen_pow_imag_min', self.max_gen_pow_imag_min_viol])
            csv_writer.writerow(['gen_pow_imag_max', self.max_gen_pow_imag_max_viol])
            csv_writer.writerow(['line_curr_orig_mag_max', self.max_line_curr_orig_mag_max_viol])
            csv_writer.writerow(['line_curr_dest_mag_max', self.max_line_curr_dest_mag_max_viol])
            csv_writer.writerow(['xfmr_pow_orig_mag_max', self.max_xfmr_pow_orig_mag_max_viol])
            csv_writer.writerow(['xfrm_pow_dest_mag_max', self.max_xfmr_pow_dest_mag_max_viol])
            csv_writer.writerow(['swsh_adm_imag_min', self.max_swsh_adm_imag_min_viol])
            csv_writer.writerow(['swsh_adm_imag_max', self.max_swsh_adm_imag_max_viol])
            csv_writer.writerow(['bus_pow_balance_real', self.max_bus_pow_balance_real_viol])
            csv_writer.writerow(['bus_pow_balance_imag', self.max_bus_pow_balance_imag_viol])
            csv_writer.writerow(['bus_ctg_volt_mag_min', self.max_bus_ctg_volt_mag_min_viol])
            csv_writer.writerow(['bus_ctg_volt_mag_max', self.max_bus_ctg_volt_mag_max_viol])
            csv_writer.writerow(['gen_ctg_pow_real_min', self.max_gen_ctg_pow_real_min_viol])
            csv_writer.writerow(['gen_ctg_pow_real_max', self.max_gen_ctg_pow_real_max_viol])
            csv_writer.writerow(['gen_ctg_pow_imag_min', self.max_gen_ctg_pow_imag_min_viol])
            csv_writer.writerow(['gen_ctg_pow_imag_max', self.max_gen_ctg_pow_imag_max_viol])
            csv_writer.writerow(['line_ctg_curr_orig_mag_max', self.max_line_ctg_curr_orig_mag_max_viol])
            csv_writer.writerow(['line_ctg_curr_dest_mag_max', self.max_line_ctg_curr_dest_mag_max_viol])
            csv_writer.writerow(['xfmr_ctg_pow_orig_mag_max', self.max_xfmr_ctg_pow_orig_mag_max_viol])
            csv_writer.writerow(['xfmr_ctg_pow_dest_mag_max', self.max_xfmr_ctg_pow_dest_mag_max_viol])
            csv_writer.writerow(['swsh_ctg_adm_imag_min', self.max_swsh_ctg_adm_imag_min_viol])
            csv_writer.writerow(['swsh_ctg_adm_imag_max', self.max_swsh_ctg_adm_imag_max_viol])
            csv_writer.writerow(['bus_ctg_pow_balance_real', self.max_bus_ctg_pow_balance_real_viol])
            csv_writer.writerow(['bus_ctg_pow_balance_imag', self.max_bus_ctg_pow_balance_imag_viol])
            csv_writer.writerow(['gen_ctg_pvpq1', self.max_gen_ctg_pvpq1_viol])
            csv_writer.writerow(['gen_ctg_pvpq2', self.max_gen_ctg_pvpq2_viol])
            
            self.write_bus_base_violations(csv_writer)
            
            self.write_gen_base_violations(csv_writer)
            
            self.write_line_base_violations(csv_writer)
            
            self.write_transformer_base_violations(csv_writer)

            self.write_swsh_base_violations(csv_writer)
                        
            self.write_bus_contingencies(csv_writer)
            
            
            '''
            start_time = time.time()
            csv_writer.writerows(
                [[i, k, self.bus_ctg_volt_mag_min_viol[(i,k)], self.bus_ctg_volt_mag_max_viol[(i,k)],
                  self.bus_ctg_pow_balance_real_viol[(i,k)], self.bus_ctg_pow_balance_imag_viol[(i,k)]]
                 for i in self.bus
                 for k in self.ctg])
            time_elapsed = time.time() - start_time
            print 'write bus ctg time (2): %u' % time_elapsed
            start_time = time.time()
            bus_ctg_viol = [
                [i, k, self.bus_ctg_volt_mag_min_viol[(i,k)], self.bus_ctg_volt_mag_max_viol[(i,k)],
                 self.bus_ctg_pow_balance_real_viol[(i,k)], self.bus_ctg_pow_balance_imag_viol[(i,k)]]
                for i in self.bus
                for k in self.ctg]
            time_elapsed = time.time() - start_time
            print 'build bus_ctg_viol time: %u' % time_elapsed
            start_time = time.time()
            csv_writer.writerows(bus_ctg_viol)
            time_elapsed = time.time() - start_time
            print 'write bus ctg time (3): %u' % time_elapsed
            '''
            
            self.write_gen_contingencies(csv_writer)
            
            self.write_line_contingencies(csv_writer)
            
            self.write_transformer_contingencies(csv_writer)
            
            self.write_swsh_contingencies(csv_writer)
            

def solution_read_sections(file_name, section_start_line_str=None, has_headers=None):

    with open(file_name, 'r') as in_file:
        lines = in_file.readlines()
    sections = solution_read_sections_from_lines(lines, section_start_line_str, has_headers)
    return sections

def solution_read_sections_from_lines(lines, section_start_line_str=None, has_headers=None):

    if section_start_line_str is None:
        section_start_line_str = '--'
    if has_headers is None:
        has_headers = True
    num_lines = len(lines)
    delimiter_str = ","
    quote_str = "'"
    skip_initial_space = True
    lines = csv.reader(
        lines,
        delimiter=delimiter_str,
        quotechar=quote_str,
        skipinitialspace=skip_initial_space)
    lines = [[t.strip() for t in r] for r in lines]
    lines = [r for r in lines if len(r) > 0]
    section_start_line_nums = [
        i for i in range(num_lines)
        if lines[i][0][:2] == section_start_line_str]
    num_sections = len(section_start_line_nums)
    section_end_line_nums = [
        section_start_line_nums[i]
        for i in range(1,num_sections)]
    section_end_line_nums += [num_lines]
    section_start_line_nums = [
        section_start_line_nums[i] + 1
        for i in range(num_sections)]
    if has_headers:
        section_start_line_nums = [
            section_start_line_nums[i] + 1
            for i in range(num_sections)]
    sections = [
        [lines[i]
         for i in range(
                 section_start_line_nums[j],
                 section_end_line_nums[j])]
        for j in range(num_sections)]
    return sections
        
class Solution1:
    '''In physical units, i.e. data convention, i.e. same as input and output data files'''

    def __init__(self):
        '''items to be read from solution1.txt'''

        self.bus_volt_mag = {}
        self.bus_volt_ang = {}
        self.bus_swsh_adm_imag = {}
        self.gen_pow_real = {}
        self.gen_pow_imag = {}

    def read(self, file_name):

        bus = 0
        gen = 1
        section_start_line_str = '--'
        has_headers = True
        sections = solution_read_sections(file_name, section_start_line_str, has_headers)
        self.read_bus_rows(sections[bus])
        self.read_gen_rows(sections[gen])
            
    def read_bus_rows(self, rows):

        i = 0
        vm = 1
        va = 2
        b = 3
        for r in rows:
            ri = int(r[i])
            rvm = float(r[vm])
            rva = float(r[va])
            rb = float(r[b])
            self.bus_volt_mag[ri] = rvm
            self.bus_volt_ang[ri] = rva
            self.bus_swsh_adm_imag[ri] = rb

    def read_gen_rows(self, rows):

        i = 0
        id = 1
        p = 2
        q = 3
        for r in rows:
            ri = int(r[i])
            rid = str(r[id])
            rp = float(r[p])
            rq = float(r[q])
            self.gen_pow_real[(ri,rid)] = rp
            self.gen_pow_imag[(ri,rid)] = rq

class Solution2:
    '''In physical units, i.e. data convention, i.e. same as input and output data files'''

    def __init__(self):
        '''items to be read from solution2.txt'''

        self.ctg_label = ""
        self.bus_volt_mag = {}
        self.bus_volt_ang = {}
        self.bus_swsh_adm_imag = {}
        self.gen_pow_real = {}
        self.gen_pow_imag = {}
        self.pow_real_change = 0.0

    def display(self):

        print "ctg_label: %s" % self.ctg_label
        print "bus_volt_mag:"
        print self.bus_volt_mag
        print "bus_volt_ang:"
        print self.bus_volt_ang
        print "bus_swsh_adm_imag:"
        print self.bus_swsh_adm_imag
        print "gen_pow_real:"
        print self.gen_pow_real
        print "gen_pow_imag:"
        print self.gen_pow_imag
        print "pow_real_change:"
        print self.pow_real_change
        
    def read_from_lines(self, lines):
        """read a sol2 object from a list of text lines
        the lines may be selected as a single contingency from a file
        containing multiple contingencies"""

        con = 0
        bus = 1
        gen = 2
        delta = 3
        section_start_line_str = '--'
        has_headers = True
        sections = solution_read_sections_from_lines(lines, section_start_line_str, has_headers)
        self.read_con_rows(sections[con])
        self.read_bus_rows(sections[bus])
        self.read_gen_rows(sections[gen])
        self.read_delta_rows(sections[delta])

    def read_con_rows(self, rows):

        k = 0
        assert(len(rows) == 1)
        r = rows[0]
        rk = str(r[k])
        self.ctg_label = rk

    def read_bus_rows(self, rows):

        i = 0
        vm = 1
        va = 2
        b = 3
        for r in rows:
            ri = int(r[i])
            rvm = float(r[vm])
            rva = float(r[va])
            rb = float(r[b])
            self.bus_volt_mag[ri] = rvm
            self.bus_volt_ang[ri] = rva
            self.bus_swsh_adm_imag[ri] = rb

    def read_gen_rows(self, rows):

        i = 0
        id = 1
        p = 2
        q = 3
        for r in rows:
            ri = int(r[i])
            rid = str(r[id])
            rp = float(r[p])
            rq = float(r[q])
            self.gen_pow_real[(ri,rid)] = rp
            self.gen_pow_imag[(ri,rid)] = rq

    def read_delta_rows(self, rows):

        p = 0
        assert(len(rows) == 1)
        r = rows[0]
        rp = float(r[p])
        self.pow_real_change = rp

def trans_old(raw_name, rop_name, con_name, inl_nsame,filename):

    # read the data files
    p = data.Data()
    p.raw.read(raw_name)
    if rop_name[-3:]=='csv':
        p.rop.read_from_phase_0(rop_name)
        p.rop.trancostfuncfrom_phase_0(p.raw)
        p.rop.write(filename+".rop",p.raw)
        p.con.read_from_phase_0(con_name)
        p.con.write(filename+".con")
        p.inl.write(filename+".inl",p.raw,p.rop)
    




# run method with reading some data from phase 0
def run_old(raw_name, rop_name, con_name, inl_name, sol1_name, sol2_name, summary_name, detail_name):

    # read the data files
    p = data.Data()
    p.raw.read(raw_name)
    if rop_name[-3:]=='rop':
        p.rop.read(rop_name)
        p.con.read(con_name)
        p.inl.read(inl_name)
    elif rop_name[-3:]=='csv':
        p.rop.read_from_phase_0(rop_name)
        p.rop.trancostfuncfrom_phase_0(p.raw)
        p.rop.write("C:\SyncDrive\PNNL_Project\ACOPF Competition\eval_phase1\\testfile.rop",p.raw)
        p.con.read_from_phase_0(con_name)
        p.con.write("C:\SyncDrive\PNNL_Project\ACOPF Competition\eval_phase1\\testfile2.con")
        p.inl.write("C:\SyncDrive\PNNL_Project\ACOPF Competition\eval_phase1\\testfile3.inl",p.raw,p.rop)
    
    print "buses: %u" % len(p.raw.buses)
    print "loads: %u" % len(p.raw.loads)
    print "fixed_shunts: %u" % len(p.raw.fixed_shunts)
    print "generators: %u" % len(p.raw.generators)
    print "nontransformer_branches: %u" % len(p.raw.nontransformer_branches)
    print "transformers: %u" % len(p.raw.transformers)
    print "areas: %u" % len(p.raw.areas) # should do areas
    print "switched_shunts: %u" % len(p.raw.switched_shunts)
    print "generator inl records: %u" % len(p.inl.generator_inl_records)
    print "generator dispatch records: %u" % len(p.rop.generator_dispatch_records)
    print "active power dispatch records: %u" % len(p.rop.active_power_dispatch_records)
    print "piecewise linear cost functions: %u" % len(p.rop.piecewise_linear_cost_functions)
    print 'contingencies: %u' % len(p.con.contingencies)

    s1 = Solution1()
    s2 = Solution2()
    s1.read(sol1_name)
    s2.read(sol2_name) # todo skip solution2 for now
    #print 'solution 1'
    #print 'gen pow real'
    #print s1.gen_pow_real
    #print 'solution 2'
    #print 'area ctg pow real delta'
    #print s2.area_ctg_pow_real_change

    e = Evaluation()
    e.set_data(p)
    e.set_solution1(s1)
    e.set_solution2(s2) # todo skip solution2 for now
    e.evaluate()
    e.normalize()
    e.compute_summary()
    #e.write_summary(summary_name) # probably do not need this
    e.write_detail(detail_name)
    print 'obj: %12.6e, cost: %12.6e, penalty: %12.6e, max nonobj viol: %12.6e' % (e.obj, e.cost, e.penalty, e.max_nonobj_viol)
    return (e.obj, e.cost, e.penalty, e.max_nonobj_viol)



def get_bus_volt_mag_min_viol(raw_name):
    for row in self.get_row(raw_name):
        row = pad_row(row, 13)
        nvlo = parse_token(row[10], float, 0.9)
    
    

def run(raw_name, rop_name, con_name, inl_name, sol1_name, sol2_name, summary_name, detail_name, scenario_number, runtime_sec):

    # read the data files
    p = data.Data()

    # read raw
    start_time = time.time()
    p.raw.read(raw_name)
    time_elapsed = time.time() - start_time
    print "read raw time: %u" % time_elapsed

    # read rop
    start_time = time.time()
    p.rop.read(rop_name)
    time_elapsed = time.time() - start_time
    print "read rop time: %u" % time_elapsed

    # read con
    start_time = time.time()
    p.con.read(con_name)
    time_elapsed = time.time() - start_time
    print "read con time: %u" % time_elapsed

    # read inl
    start_time = time.time()
    p.inl.read(inl_name)
    time_elapsed = time.time() - start_time
    print "read inl time: %u" % time_elapsed

    # show data stats
    print "buses: %u" % len(p.raw.buses)
    print "loads: %u" % len(p.raw.loads)
    print "fixed_shunts: %u" % len(p.raw.fixed_shunts)
    print "generators: %u" % len(p.raw.generators)
    print "nontransformer_branches: %u" % len(p.raw.nontransformer_branches)
    print "transformers: %u" % len(p.raw.transformers)
    print "areas: %u" % len(p.raw.areas)
    print "switched_shunts: %u" % len(p.raw.switched_shunts)
    print "generator inl records: %u" % len(p.inl.generator_inl_records)
    print "generator dispatch records: %u" % len(p.rop.generator_dispatch_records)
    print "active power dispatch records: %u" % len(p.rop.active_power_dispatch_records)
    print "piecewise linear cost functions: %u" % len(p.rop.piecewise_linear_cost_functions)
    print 'contingencies: %u' % len(p.con.contingencies)

    # read the solution
    s1 = Solution1()
    s2 = Solution2()

    # read sol 1
    start_time = time.time()
    s1.read(sol1_name)
    time_elapsed = time.time() - start_time
    print "read sol1 time: %u" % time_elapsed

    # read sol 2
    start_time = time.time()
    s2.read(sol2_name)
    time_elapsed = time.time() - start_time
    print "read sol2 time: %u" % time_elapsed

    # add data and solution to evaluation
    e = Evaluation()
    
    e.scenario_number = scenario_number
    e.runtime_sec = runtime_sec

    # set eval data
    start_time = time.time()
    e.set_data(p)
    time_elapsed = time.time() - start_time
    print "eval set data time: %u" % time_elapsed

    # set eval sol1
    start_time = time.time()
    e.set_solution1(s1)
    time_elapsed = time.time() - start_time
    print "eval set sol1 time: %u" % time_elapsed

    # eval set sol2
    start_time = time.time()
    e.set_solution2(s2)
    time_elapsed = time.time() - start_time
    print "eval set sol2 time: %u" % time_elapsed

    # evaluate
    start_time = time.time()
    e.set_params() # convert to per unit for evaluation - this might not be the right place to put this item
    e.evaluate()
    time_elapsed = time.time() - start_time
    print "evaluate time: %u" % time_elapsed

    # normalize
    start_time = time.time()
    e.normalize()
    time_elapsed = time.time() - start_time
    print "eval normalize time: %u" % time_elapsed

    # compute summary
    start_time = time.time()
    e.compute_summary()
    time_elapsed = time.time() - start_time
    print "eval compute summary time: %u" % time_elapsed

    # convert to data units
    start_time = time.time()
    e.convert_to_data_units()
    time_elapsed = time.time() - start_time
    print "eval convert to data units time: %u" % time_elapsed

    # write summary
    #start_time = time.time()
    #e.write_summary(summary_name) # probably do not need this
    #time_elapsed = time.time() - start_time
    #print "eval write summary time: %u" % time_elapsed

    # write detail
    start_time = time.time()
    e.write_detail(detail_name)
    time_elapsed = time.time() - start_time
    print "eval write detail time: %u" % time_elapsed

    # some results
    print 'obj: %12.6e, cost: %12.6e, penalty: %12.6e, max nonobj viol: %12.6e' % (e.obj, e.cost, e.penalty, e.max_nonobj_viol)
    
    e.write_summary(summary_name)
    
    return (e.obj, e.cost, e.penalty, e.max_nonobj_viol)

# old run method
#def run(raw_name, rop_name, con_name, inl_name, sol1_name, sol2_name):
#    '''temporary stub for integration with other GOComp codes.
#    The real run() method is developed in run_old() until it is ready.'''
#
#    return (MAXOBJ, MAXVIOL)

def run(raw_name, rop_name, con_name, inl_name, sol1_name, sol2_name, det_name):

    # read the data files
    p = data.Data()

    # read raw
    start_time = time.time()
    p.raw.read(raw_name)
    time_elapsed = time.time() - start_time
    print "read raw time: %u" % time_elapsed

    # read rop
    start_time = time.time()
    p.rop.read(rop_name)
    time_elapsed = time.time() - start_time
    print "read rop time: %u" % time_elapsed

    # read con
    start_time = time.time()
    p.con.read(con_name)
    time_elapsed = time.time() - start_time
    print "read con time: %u" % time_elapsed

    # read inl
    start_time = time.time()
    p.inl.read(inl_name)
    time_elapsed = time.time() - start_time
    print "read inl time: %u" % time_elapsed

    # show data stats
    print "buses: %u" % len(p.raw.buses)
    print "loads: %u" % len(p.raw.loads)
    print "fixed_shunts: %u" % len(p.raw.fixed_shunts)
    print "generators: %u" % len(p.raw.generators)
    print "nontransformer_branches: %u" % len(p.raw.nontransformer_branches)
    print "transformers: %u" % len(p.raw.transformers)
    print "areas: %u" % len(p.raw.areas)
    print "switched_shunts: %u" % len(p.raw.switched_shunts)
    print "generator inl records: %u" % len(p.inl.generator_inl_records)
    print "generator dispatch records: %u" % len(p.rop.generator_dispatch_records)
    print "active power dispatch records: %u" % len(p.rop.active_power_dispatch_records)
    print "piecewise linear cost functions: %u" % len(p.rop.piecewise_linear_cost_functions)
    print 'contingencies: %u' % len(p.con.contingencies)

    # set up solution objects
    s1 = Solution1()
    s2 = Solution2()

    # read sol1
    start_time = time.time()
    s1.read(sol1_name)
    time_elapsed = time.time() - start_time
    print "read sol_base time: %u" % time_elapsed

    # set up evaluation
    e = Evaluation()

    # set eval data
    start_time = time.time()
    e.set_data(p)
    time_elapsed = time.time() - start_time
    print "set data time: %u" % time_elapsed

    # set penalty params (later read from case.prm)
    start_time = time.time()
    e.set_params()
    time_elapsed = time.time() - start_time
    print "set params time: %u" % time_elapsed

    # set eval sol1
    start_time = time.time()
    e.set_solution1(s1)
    time_elapsed = time.time() - start_time
    print "set sol1 time: %u" % time_elapsed

    # evaluate base
    start_time = time.time()
    e.eval_base()
    time_elapsed = time.time() - start_time
    print "eval base time: %u" % time_elapsed
    
    # write base summary
    start_time = time.time()
    e.write_header(det_name)
    e.write_base(det_name)
    time_elapsed = time.time() - start_time
    print "write base time: %u" % time_elapsed

    # get ctg structure in sol
    # do not forget to check that every contingency is found in the sol file
    ctg_num_lines = get_ctg_num_lines(sol2_name)
    num_ctgs = len(ctg_num_lines)
    with open(sol2_name) as sol2_file:
        for k in range(num_ctgs):
            lines = list(islice(sol2_file, ctg_num_lines[k]))
            if not lines:
                break # error
            s2.read_from_lines(lines)
            e.set_solution2(s2)
            e.set_ctg_data()
            e.eval_ctg()
            e.write_ctg(det_name)
        
    return (e.obj, e.cost, e.penalty, e.max_nonobj_viol)
    return (0.0, 0.0, 0.0, 0.0, 0.0)
