from firedrake import *  # noqa: F403
import numpy

# Corners of the box.
x0 = 0.0
x1 = 2.2
y0 = 0.0
y1 = 0.41

#Mesh
stepfile = "circle.step"
h = 0.1 # Close to what Turek's benchmark has on coarsest mesh
order = 2
lvl=3
mh = OpenCascadeMeshHierarchy(stepfile, element_size=h,
                              levels=lvl, order=order, cache=False,
                              verbose=True)

msh = mh[-1]

#CG1 = FunctionSpace(msh, "CG", 1)
#bcvals = Function(CG1)
#for i in range(1, 6):
#    DirichletBC(CG1, i, i).apply(bcvals)
#File("/tmp/colours.pvd").write(bcvals)

V = VectorFunctionSpace(msh, "CG", 2)
W = FunctionSpace(msh, "DG", 0)
Z = V * W

v, w = TestFunctions(Z)
x, y = SpatialCoordinate(msh)

up = Function(Z)
u, p = split(up)

n= FacetNormal(msh)

nu = Constant(0.001)
rho=1.0
r=0.05
Umean=0.2
L=0.1

# define the variational form once outside the loop
F = (inner(dot(grad(u), u), v) * dx
     + nu * inner(grad(u), grad(v)) * dx
     - inner(p, div(v)) * dx
     + inner(div(u), w) * dx)

# boundary conditions are specified for each subspace
UU = Constant(0.3)
bcs = [DirichletBC(Z.sub(0),
                   as_vector([4 * UU * y * (y1 - y) / (y1**2), 0]), (4,)),
       DirichletBC(Z.sub(0), Constant((0, 0)), (1, 3, 5))]

s_param={'ksp_type': 'preonly',
         'pc_type': 'lu',
         'pc_factor_shift_type': 'inblocks',
         'mat_type': 'aij',
         'snes_max_it': 100,
         'snes_monitor': None}


ut1 = dot(u, as_vector([n[1], -n[0]]))

solve(F==0, up, bcs=bcs, solver_parameters=s_param)

FD = assemble(-(nu*dot(grad(ut1), n)*n[1] - p*n[0])*ds(5) )
FL = assemble(-(nu*inner(grad(ut1), n)*n[0]-p*n[1])*ds(5) )

CD = [2 * FD / (Umean**2) / L] #Drag coefficient
CL = [2 * FL / (Umean**2) / L] #Lift coefficient

print("Level", lvl)
print("CD", CD)
print("CL", CL)

u, p = up.split()
File("nse_stead.pvd").write(u, p)