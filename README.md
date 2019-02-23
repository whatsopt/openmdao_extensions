# OpenMDAO Extensions

Set of specialized classes to handle specific methods using OpenMDAO framework.

* <code>OneraSegoDriver</code> : an OpenMDAO driver for Onera Super EGO optimizers 
* <code>SmtDoeDriver</code> : an OpenMDAO driver for LHS DoE from surrogate library [SMT](https://smt.readthedocs.io/en/latest/)
* <code>SalibDoeDriver</code> : an OpenMDAO driver for Morris DoE from sensitive anaysis library [SALib](https://salib.readthedocs.io/en/latest/)
* <code>RecklessNonlinearBlockGS</code> : a specialized version of NonlinearBlockGS solver to handle convergence variables specifications.

# Installation
```
pip install git+https://github.com/OneraHub/openmdao_extensions.git
```
