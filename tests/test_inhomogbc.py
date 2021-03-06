import pytest
from firedrake import *
from ufl.algorithms.ad import expand_derivatives
from irksome import GaussLegendre, Dt, TimeStepper


def heat_inhomog(N, deg, butcher_tableau):
    dt = Constant(1.0 / N)
    t = Constant(0.0)

    msh = UnitSquareMesh(N, N)

    V = FunctionSpace(msh, "CG", 1)
    x, y = SpatialCoordinate(msh)

    uexact = t*(x+y)
    rhs = expand_derivatives(diff(uexact, t)) - div(grad(uexact))

    u = interpolate(uexact, V)

    v = TestFunction(V)
    F = inner(Dt(u), v)*dx + inner(grad(u), grad(v))*dx - inner(rhs, v)*dx

    bc = DirichletBC(V, uexact, "on_boundary")

    luparams = {"mat_type": "aij",
                "snes_type": "ksponly",
                "ksp_type": "preonly",
                "pc_type": "lu"}

    stepper = TimeStepper(F, butcher_tableau, t, dt, u, bcs=bc,
                          solver_parameters=luparams)

    while (float(t) < 1.0):
        if (float(t) + float(dt) > 1.0):
            dt.assign(1.0 - float(t))
        stepper.advance()
        t.assign(float(t) + float(dt))

    return norm(u-uexact)


@pytest.mark.parametrize(('deg', 'N', 'time_stages'),
                         [(1, 2**j, i) for j in range(2, 4)
                          for i in (1, 2)]
                         + [(2, 2**j, i) for j in range(2, 4)
                            for i in (2, 3)])
def test_inhomog_bc(deg, N, time_stages):
    error = heat_inhomog(N, deg, GaussLegendre(time_stages))
    assert abs(error) < 1e-10
