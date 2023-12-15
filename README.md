[![Tests](https://github.com/OneraHub/openmdao_extensions/workflows/Tests/badge.svg)](https://github.com/OneraHub/openmdao_extensions/actions?query=workflow%3ATests)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/54f346b4094a42f081c4f674e2990aee)](https://app.codacy.com/gh/whatsopt/openmdao_extensions/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# OpenMDAO Extensions

Set of specialized classes to handle specific methods using OpenMDAO framework.

*   <code>EgoboxEgorDriver</code> : an OpenMDAO driver for Egor optimizer from [Egobox](https://github.com/relf/egobox#egobox) library 
*   <code>EgoboxDOEDriver</code> : an OpenMDAO driver for Mixint LHS DoE from [Egobox](https://github.com/relf/egobox#egobox) library 
*   <code>OneraSegoDriver</code> : an OpenMDAO driver for Onera Super EGO optimizers 
*   <code>SmtDOEDriver</code> : an OpenMDAO driver for sampling methods from surrogate [SMT](https://smt.readthedocs.io/en/latest/) library 
*   <code>SalibDOEDriver</code> : an OpenMDAO driver for Morris or Saltelli DoE from sensitive analysis [SALib](https://salib.readthedocs.io/en/latest/) library 
*   <code>OpenturnsDoeDriver</code> : an OpenMDAO driver for DoE following distributions from [OpenTURNS](http://www.openturns.org/) library
*   <code>RecklessNonlinearBlockGS</code> : a specialized version of the `NonlinearBlockGS` solver to select variables used in the convergence criterion.

## Installation
```bash
pip install openmdao-extensions
```

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
