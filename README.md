# OpenMDAO Extensions

Set of specialized classes to handle specific methods using OpenMDAO framework.

* <code>OneraSegoDriver</code> : an OpenMDAO driver for Onera Super EGO optimizers 
* <code>SmtDoeDriver</code> : an OpenMDAO driver for LHS DoE from surrogate library [SMT](https://smt.readthedocs.io/en/latest/)
* <code>SalibDoeDriver</code> : an OpenMDAO driver for Morris DoE from sensitive anaysis library [SALib](https://salib.readthedocs.io/en/latest/)
* <code>RecklessNonlinearBlockGS</code> : a specialized version of NonlinearBlockGS solver to handle convergence variables specifications.

## Installation
```
pip install git+https://github.com/OneraHub/openmdao_extensions.git
```

## Compatibility

* 0.1 : OpenMDAO <= 2.6, SALib 1.1.3, SMT 0.2
* 0.2 : OpenMDAO <= 2.6, SALib 1.3.3, SMT 0.2

## License

   Copyright 2019 Rémi Lafage

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

