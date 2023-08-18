from cosapp.base import System
from cosapp.drivers import Optimizer, NonLinearSolver
from amad.disciplines.mass.systems import WingMassSimpleAC
from amad.disciplines.aerodynamics.systems import Drag
from amad.disciplines.systems.fuel.systems.fuelVolume import FuelVolume_Weight


class OptimizeSimpleAC(System):
    def setup(self):
        # add subsystems
        self.add_child(
            WingMassSimpleAC("wingweight"), pulling=["S", "V_f_fuse", "W", "AR"]
        )
        self.add_child(Drag("drag"), pulling=["AR", "S", "V", "V_f_fuse", "C_L"])
        self.add_child(
            FuelVolume_Weight("fuelvol"), pulling=["AR", "S", "V_f_fuse", "W_f"]
        )

        # define inwards (constants)
        self.add_inward("W_0", 6250, desc="aircraft empty weight excluding wing, N")
        self.add_inward("rho", 1.23, desc="density of air, kg/m^3")
        self.add_inward("V_min", 25, desc="takeoff speed, m/s")
        self.add_inward("C_Lmax", 1.6, desc="stall CL")
        self.add_inward(
            "TSFC",
            1.666666666666666666666e-4,
            desc="thrust specific fuel consumption, 1/sec",
        )
        self.add_inward("Range", 1000e3, desc="ac range")

        # define outwards (calculated parameters within this system)
        self.add_outward("Lift_CR")
        self.add_outward("Lift_TO")
        self.add_outward("T_flight")

    def compute(self):
        self.Lift_CR = 0.5 * self.rho * self.S * self.C_L * (self.V**2)
        self.Lift_TO = 0.5 * self.rho * self.S * self.C_Lmax * (self.V_min**2)
        self.T_flight = self.Range / self.V
        # self.W_f = self.TSFC * self.T_flight * self.drag.total.force
        # self.W = self.W_0 + self.wingweight.total.mass + self.W_f


if __name__ == "__main__":
    acmodel = OptimizeSimpleAC("opti")
    # print(acmodel.to_dict())
    opti = acmodel.add_driver(Optimizer("optimization", method="SLSQP"))

    opti = opti
    # opti = opti.runner  # cosapp < 0.12.1
    opti.add_child(NonLinearSolver("nls"))

    # Initial Guesses:
    # """
    acmodel.V_f_fuse = 1.0
    acmodel.AR = 10.0
    acmodel.W = 6250.0
    acmodel.S = 10.0
    acmodel.V = 100.0
    acmodel.W_f = 3000.0
    acmodel.C_L = 1.0
    # """

    # define unknowns
    opti.add_unknown("V_f_fuse", lower_bound=0.0, upper_bound=999.0)
    opti.add_unknown("AR", lower_bound=1.0, upper_bound=30.0)
    opti.add_unknown("W", lower_bound=3000.0, upper_bound=99999.0)
    opti.add_unknown("S", lower_bound=1.0, upper_bound=999.0)
    opti.add_unknown("V", lower_bound=50.0, upper_bound=999.0)
    opti.add_unknown("W_f", lower_bound=1.0, upper_bound=9999.0)
    opti.add_unknown("C_L", lower_bound=0.01, upper_bound=2.0)

    # cosapp < 0.12.1 :
    # opti.add_constraints([
    #     'fuelvol.available.volume - fuelvol.total.volume',    # fuelvol_avail >= fuelvol_total
    #     'W - (W_0 + wingweight.total.mass + W_f)',    # W >= W_0 + W_w + W_f
    #     '(0.5 * rho * S * C_L * V**2) - (W_0 + wingweight.total.mass + 0.5 * W_f) ',  # W_0 + W_w + 0.5 * W_f <= 0.5 * rho * S * C_L * V ** 2
    #     'W_f - (TSFC * T_flight * drag.total.force)',  # W_f >= TSFC * T_flight * D
    #     '(0.5 * rho * S * C_Lmax * V_min**2) - W'  # W <= 0.5 * rho * S * C_Lmax * V_min ** 2
    # ])

    opti.add_constraints(
        [
            "fuelvol.available.volume >= fuelvol.total.volume",  # fuelvol_avail >= fuelvol_total
            "W >= (W_0 + wingweight.total.mass + W_f)",  # W >= W_0 + W_w + W_f
            "(W_0 + wingweight.total.mass + 0.5 * W_f) <= (0.5 * rho * S * C_L * V**2)",  # W_0 + W_w + 0.5 * W_f <= 0.5 * rho * S * C_L * V ** 2
            "W_f >= (TSFC * T_flight * drag.total.force)",  # W_f >= TSFC * T_flight * D
            "(0.5 * rho * S * C_Lmax * V_min**2) >= W",  # W <= 0.5 * rho * S * C_Lmax * V_min ** 2
        ]
    )

    opti.set_objective("W_f")  # minimize W_f
    acmodel.run_drivers()

    print(f"AR:  {acmodel.AR:.4f}, REF: 12.1049")
    print(f"S:   {acmodel.S:.4f},  REF: 14.1542")
    print(f"V:   {acmodel.V:.3f},  REF: 57.106")
    print(f"W:   {acmodel.W:.2f},  REF: 8704.82")
    print(f"C_L: {acmodel.C_L:.6f},  REF: 0.290128")
    print(f"W_f: {acmodel.W_f:.3f},  REF: 937.756")
    print(f"V_f_fuse: {acmodel.V_f_fuse:.7f},  REF: 0.0619038")
    print(f"Lift_CR: {acmodel.Lift_CR:.1f} REF: 8235.9")
    print(f"Lift_TO: {acmodel.Lift_TO:.1f} REF: 8704.8")
    print(f"T_flight: {acmodel.T_flight:.1f},  REF: 17511.3")

    # print('Solver Problem:',opti.problem)
