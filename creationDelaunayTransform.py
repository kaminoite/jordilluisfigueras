import sys
import re
import sympy as sp
from itertools import product
from sympy.printing import StrPrinter

StrPrinter._print_Pow = lambda self, expr: "pow(%s, %s)" % (self._print(expr.base), self._print(expr.exp))
sp.init_printing(use_unicode=True, use_latex='mathjax')

def substitute_cosE(lines):
    result = []
    for line in lines:
        if line.strip() == "cosE = cos(E);":
            result.append(line)
        else:
            result.append(line.replace("cos(E)", "cosE"))
    return result

def substitute_sinE(lines):
    result = []
    for line in lines:
        if line.strip() == "sinE = sin(E);":
            result.append(line)
        else:
            result.append(line.replace("sin(E)", "sinE"))
    return result

def remove_z_and_inner_brackets_from_list(input_list):
    if not isinstance(input_list, list):
        raise TypeError("Expected a list of strings")
    
    result_list = []
    for item in input_list:
        if not isinstance(item, str):
            raise TypeError("All items in the list must be strings")
        # Use regex to find and replace the pattern [z[anything]] with [anything]
        modified_item = re.sub(r'\[z\[(.*?)\]\]', r'[\1]', item)
        result_list.append(modified_item)
    
    return result_list

def substitute_z_lambda(input_list):
    if not isinstance(input_list, list):
        raise TypeError("Expected a list of strings")
    
    result_list = []
    for item in input_list:
        if not isinstance(item, str):
            raise TypeError("All items in the list must be strings")
        # Use regex to find and replace the pattern z[Lambda?] with Lambda?
        modified_item = re.sub(r'z\[Lambda(.?)\]', r'lam\1', item)
        result_list.append(modified_item)
    
    return result_list

# Define the variables
L, l, G, g = sp.symbols('z[L] z[l] z[G] z[g]')
m = sp.symbols("m")

subsDict = {}
# List to store formatted derivatives
formatted_derivatives = []

formatted_derivatives.append(f"void DelaunayTransform(real *z, const real& m, real& x1, real& x2, real *d1x1, real *d1x2, real **d2x1, real **d2x2, real ***d3x1, real ***d3x2, real& y1, real& y2, real *d1y1, real *d1y2, real **d2y1, real **d2y2, real ***d3y1, real ***d3y2)")
formatted_derivatives.append("{")

namein="x1"
formatted_derivatives.append("int L, G, l, g;")

#GL
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("G = 1;")
formatted_derivatives.append("real GL;")
formatted_derivatives.append("real d1GL[4];")
formatted_derivatives.append("real d2GL[4][4];")
formatted_derivatives.append("real d3GL[4][4][4];")
GL = G/L
HH = GL
derivative = HH
variables = [L, G]
Hname = 'GL'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
flag = 0
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1
    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")

    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

GL = sp.Function("GL")(L, G)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({GL.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({GL.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({GL.diff(item1, item2, item3):stri})
subsDict.update({GL: Hname})

#e
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("G = 1;")
formatted_derivatives.append("real e;")
formatted_derivatives.append("real *d1e = nullptr;")
formatted_derivatives.append("real **d2e = nullptr;")
formatted_derivatives.append("real ***d3e = nullptr;")
formatted_derivatives.append("d1e = new real[4];")
formatted_derivatives.append("d2e = new real*[4];")
formatted_derivatives.append("d3e = new real**[4];")
formatted_derivatives.append("for(int i = 0; i < 4; i++)")
formatted_derivatives.append("{")
formatted_derivatives.append("d2e[i] = new real[4];")
formatted_derivatives.append("d3e[i] = new real*[4];")
formatted_derivatives.append("for(int j = 0; j < 4; j++)")
formatted_derivatives.append("{")
formatted_derivatives.append("d3e[i][j] = new real[4];")
formatted_derivatives.append("}")
formatted_derivatives.append("}")

e = sp.sqrt(1-GL**2)
HH = e
derivative = HH
variables = [L, G]
Hname = 'e'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1


    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")
    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

e = sp.Function("e")(L, G)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({e.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({e.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({e.diff(item1, item2, item3):stri})
subsDict.update({e: Hname})

#a
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("real a;")
formatted_derivatives.append("real d1a[4];")
formatted_derivatives.append("real d2a[4][4];")
formatted_derivatives.append("real d3a[4][4][4];")

a = L*L/(m*m)
HH = a
derivative = HH
variables = [L]
Hname = 'a'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")

    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

a = sp.Function("a")(L, m)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({a.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({a.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({a.diff(item1, item2, item3):stri})
subsDict.update({a: Hname})

#b
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("real b;")
formatted_derivatives.append("real d1b[4];")
formatted_derivatives.append("real d2b[4][4];")
formatted_derivatives.append("real d3b[4][4][4];")


b = m*m/L
HH = b
derivative = HH
variables = [L]
Hname = 'b'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")
    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)


b = sp.Function("b")(L, m)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({b.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({b.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({b.diff(item1, item2, item3):stri})
subsDict.update({b: Hname})

#E
formatted_derivatives.append("")
toadd = """
real E;
real *d1E = nullptr;
real **d2E = nullptr;
real ***d3E = nullptr;

d1E = new real [4];
d2E = new real* [4];
d3E = new real** [4];
for(int i = 0; i < 4; i++)
{
    d2E[i] = new real [4];
    d3E[i] = new real* [4];
    for(int j = 0; j < 4; j++)
    {
        d3E[i][j] = new real [4];
    }
}
L = 0;
G = 1;
l = 2;
derivatives_E(z[L], z[G], z[l], d1e, d2e, d3e, E, d1E, d2E, d3E);
"""
formatted_derivatives.append(toadd)
Hname = 'E'
E = sp.Function("E")(L, G, l)
variables = [L, G, l]
formatted_derivatives.append("")
subsDictE = {}

for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDictE.update({E.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDictE.update({E.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDictE.update({E.diff(item1, item2, item3):stri})
#subsDictE.update({E: Hname})
subsDict.update(subsDictE)

#cosE
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("G = 1;")
formatted_derivatives.append("l = 2;")
formatted_derivatives.append("real cosE;")
formatted_derivatives.append("real sinE;")
formatted_derivatives.append("real d1cosE[4];")
formatted_derivatives.append("real d2cosE[4][4];")
formatted_derivatives.append("real d3cosE[4][4][4];")

cosE = sp.cos(E)
HH = cosE
derivative = HH
variables = [L, G, l]
Hname = 'cosE'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
formatted_derivatives.append(f"sinE = sin(E);")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")

    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

cosE = sp.Function("cosE")(L, G, l)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({cosE.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({cosE.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({cosE.diff(item1, item2, item3):stri})
subsDict.update({cosE: Hname})

#sinE
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("G = 1;")
formatted_derivatives.append("l = 2;")
formatted_derivatives.append("real d1sinE[4];")
formatted_derivatives.append("real d2sinE[4][4];")
formatted_derivatives.append("real d3sinE[4][4][4];")

sinE = sp.sin(E)
HH = sinE
derivative = HH
variables = [L, G, l]
Hname = 'sinE'
# formatted_derivatives.append(f"{Hname} = {derivative};")
# Compute derivatives up to order 3
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")

    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)


sinE = sp.Function("sinE")(L, G, l)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({sinE.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({sinE.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({sinE.diff(item1, item2, item3):stri})
subsDict.update({sinE: Hname})

Hname = 'E'
subsDict.update({E: Hname})

#q1
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("G = 1;")
formatted_derivatives.append("l = 2;")
formatted_derivatives.append("real q1;")
formatted_derivatives.append("real d1q1[4];")
formatted_derivatives.append("real d2q1[4][4];")
formatted_derivatives.append("real d3q1[4][4][4];")

q1 = a*(cosE-e)
HH = q1
derivative = HH
variables = [L, G, l]
Hname = 'q1'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")
    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

q1 = sp.Function("q1")(L, G, l, m)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({q1.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({q1.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({q1.diff(item1, item2, item3):stri})
subsDict.update({q1: Hname})

#q2
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("G = 1;")
formatted_derivatives.append("l = 2;")
formatted_derivatives.append("real q2;")
formatted_derivatives.append("real d1q2[4];")
formatted_derivatives.append("real d2q2[4][4];")
formatted_derivatives.append("real d3q2[4][4][4];")

q2 = a*GL*sinE
HH = q2
derivative = HH
variables = [L, G, l]
Hname = 'q2'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")
    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

q2 = sp.Function("q2")(L, G, l, m)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({q2.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({q2.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({q2.diff(item1, item2, item3):stri})
subsDict.update({q2: Hname})


#cosg
formatted_derivatives.append("")
formatted_derivatives.append("g = 3;")
formatted_derivatives.append("real cosg;")
formatted_derivatives.append("real d1cosg[4];")
formatted_derivatives.append("real d2cosg[4][4];")
formatted_derivatives.append("real d3cosg[4][4][4];")

cosg = sp.cos(g)
HH = cosg
derivative = HH
variables = [g]
Hname = 'cosg'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")
    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

cosg = sp.Function("cosg")(g)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({cosg.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({cosg.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({cosg.diff(item1, item2, item3):stri})
subsDict.update({cosg: Hname})


#sing
formatted_derivatives.append("")
formatted_derivatives.append("g = 3;")
formatted_derivatives.append("real sing;")
formatted_derivatives.append("real d1sing[4];")
formatted_derivatives.append("real d2sing[4][4];")
formatted_derivatives.append("real d3sing[4][4][4];")

sing = sp.sin(g)
HH = sing
derivative = HH
variables = [g]
Hname = 'sing'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")
    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

sing = sp.Function("sing")(g)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({sing.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({sing.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({sing.diff(item1, item2, item3):stri})
subsDict.update({sing: Hname})


#x1
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("G = 1;")
formatted_derivatives.append("l = 2;")
formatted_derivatives.append("g = 3;")

x1 = cosg*q1-sing*q2
HH = x1
derivative = HH
variables = [L, G, l, g]
Hname = 'x1'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")
    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

x1 = sp.Function("x1")(L, G, l, g)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({x1.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({x1.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({x1.diff(item1, item2, item3):stri})
subsDict.update({x1: Hname})


#x2
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("G = 1;")
formatted_derivatives.append("l = 2;")
formatted_derivatives.append("g = 3;")

x2 = sing*q1+cosg*q2
HH = x2
derivative = HH
variables = [L, G, l, g]
Hname = 'x2'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")
    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

x2 = sp.Function("x2")(L, G, l, g)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({x2.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({x2.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({x2.diff(item1, item2, item3):stri})
subsDict.update({x2: Hname})


#p1
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("G = 1;")
formatted_derivatives.append("l = 2;")
formatted_derivatives.append("g = 3;")
formatted_derivatives.append("real p1;")
formatted_derivatives.append("real d1p1[4];")
formatted_derivatives.append("real d2p1[4][4];")
formatted_derivatives.append("real d3p1[4][4][4];")

p1 = b/(1-e*cosE)*(-sinE)
HH = p1
derivative = HH
variables = [L, G, l]
Hname = 'p1'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")
    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

p1 = sp.Function("p1")(L, G, l)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({p1.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({p1.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({p1.diff(item1, item2, item3):stri})
subsDict.update({p1: Hname})


#p2
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("G = 1;")
formatted_derivatives.append("l = 2;")
formatted_derivatives.append("g = 3;")
formatted_derivatives.append("real p2;")
formatted_derivatives.append("real d1p2[4];")
formatted_derivatives.append("real d2p2[4][4];")
formatted_derivatives.append("real d3p2[4][4][4];")

p2 = b/(1-e*cosE)*(GL*cosE)
HH = p2
derivative = HH
variables = [L, G, l]
Hname = 'p2'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")
    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

p2 = sp.Function("p2")(L, G, l)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({p2.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({p2.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({p2.diff(item1, item2, item3):stri})
subsDict.update({p2: Hname})


#y1
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("G = 1;")
formatted_derivatives.append("l = 2;")
formatted_derivatives.append("g = 3;")

y1 = cosg*p1-sing*p2
HH = y1
derivative = HH
variables = [L, G, l, g]
Hname = 'y1'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")
    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

y1 = sp.Function("y1")(L, G, l, g)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({y1.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({y1.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({y1.diff(item1, item2, item3):stri})
subsDict.update({y1: Hname})


#y2
formatted_derivatives.append("")
formatted_derivatives.append("L = 0;")
formatted_derivatives.append("G = 1;")
formatted_derivatives.append("l = 2;")
formatted_derivatives.append("g = 3;")

y2 = sing*p1+cosg*p2
HH = y2
derivative = HH
variables = [L, G, l, g]
Hname = 'y2'
# Compute derivatives up to order 3
formatted_derivatives.append(f"{Hname} = {derivative};")
for order in range(1, 4):
    if flag == 0 and order > 1:
        to_add = "if(d"+str(order)+namein+" != NULL)"
        formatted_derivatives.append(to_add)
        to_add = "{"
        formatted_derivatives.append(to_add)
        flag = 1

    for vars in product(variables, repeat = order):
        derivative = sp.diff(HH, *vars)
        var_str = ''.join([f"[{var}]" for var in vars])
        formatted_derivatives.append(f"d{order}{Hname}{var_str} = {derivative};")
    flag = 0

for order in range(2, 4):
    to_add = "}"
    formatted_derivatives.append(to_add)

y2 = sp.Function("y2")(L, G, l, g)
for item1 in variables:
    stri = f'd1{Hname}[{item1}]'
    subsDict.update({y2.diff(item1):stri})
    for item2 in variables:
        stri = f'd2{Hname}[{item1}][{item2}]'
        subsDict.update({y2.diff(item1, item2):stri})
        for item3 in variables:
            stri = f'd3{Hname}[{item1}][{item2}][{item3}]'
            subsDict.update({y2.diff(item1, item2, item3):stri})
subsDict.update({y2: Hname})

toadd = """
for(int i = 0; i < 4; i++)
{
    for(int j = 0; j < 4; j++)
    {
        delete [] d3E[i][j];
        delete [] d3e[i][j];
    }
    delete [] d3E[i];
    delete [] d2E[i];
    delete [] d3e[i];
    delete [] d2e[i];
}

delete [] d3E;
delete [] d2E;
delete [] d1E;
delete [] d3e;
delete [] d2e;
delete [] d1e;
"""
formatted_derivatives.append(toadd)

formatted_derivatives.append("")
formatted_derivatives.append("return ;")
formatted_derivatives.append("}")

#Substitute subsDict for the derivatives
midList = []
for item in formatted_derivatives:
    auxstr = item
    for key, value in subsDict.items():
#        print(auxstr+" "+repr(key)+" "+value)
        auxstr = auxstr.replace(repr(key), value)
#        print(auxstr)
#        print()
    midList.append(auxstr)

# Write the formatted derivatives to a file
out_derivatives = remove_z_and_inner_brackets_from_list(midList)
out_derivatives = substitute_cosE(out_derivatives)
out_derivatives = substitute_sinE(out_derivatives)

with open('DelaunayTransform.cpp', 'w') as file:
    file.write('\n'.join(out_derivatives))


file_name = 'DelaunayTransform.cpp'

# Read the content of the file
with open(file_name, 'r') as file:
    content = file.read()

# Use regex to replace pow(***, 2) with sqr(***)
# This pattern captures any expression before the comma
updated_content = content
def replace_pow_with_sqr(expression):
    import re

    def find_innermost_pow(expr):
        stack = []
        positions = []

        for i, char in enumerate(expr):
            if expr[i:i+4] == 'pow(':
                stack.append(i)
            elif char == ')' and stack:
                start = stack.pop()
                end = i
                # Check if this is a pow(..., 2) expression
                content = expr[start+4:end]
                parts = content.rsplit(',', 1)
                if len(parts) == 2 and parts[1].strip() == '2':
                    positions.append((start, end))
        return positions

    while True:
        positions = find_innermost_pow(expression)
        if not positions:
            break
        # Replace from the last to avoid messing up indices
        for start, end in reversed(positions):
            inner = expression[start+4:end]
            arg = inner.rsplit(',', 1)[0].strip()
            expression = expression[:start] + f'sqr({arg})' + expression[end+1:]

    return expression

updated_content = replace_pow_with_sqr(updated_content)

#updated_content = re.sub(r'pow\(([^,]+),\s*2\)', r'sqr(\1)', updated_content)

# Replace pow(***, -1) with val1/***
updated_content = re.sub(r'pow\(([^,]+),\s*-1\)', r'1/(\1)', updated_content)

# Replace pow(***, 3) with *** * sqr(***)
#updated_content = re.sub(r'pow\(([^,]+),\s*3\)', r'(sqr(\1)*\1)', updated_content)

# Replace pow(***, 4) with sqr(sqr(***))
#updated_content = re.sub(r'pow\(([^,]+),\s*4\)', r'sqr(sqr(\1))', updated_content)

# Replace pow(***, 1/2) with sqrt(***)
updated_content = re.sub(r'pow\(([^,]+),\s1/2\)', r'sqrt(\1)', updated_content)

# Write the updated content back to the file
with open(file_name, 'w') as file:
    file.write(updated_content)

print(f"Updated '{file_name}' with sqr(***) substitutions.")


