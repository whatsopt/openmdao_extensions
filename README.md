[![Build Status](https://travis-ci.org/relf/openmdao_extensions.svg?branch=master)](https://travis-ci.org/relf/openmdao_extensions)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/OneraHub/openmdao_extensions.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/OneraHub/openmdao_extensions/context:python)

# OpenMDAO Extensions

Set of specialized classes to handle specific methods using OpenMDAO framework.

* <code>OneraSegoDriver</code> : an OpenMDAO driver for Onera Super EGO optimizers 
* <code>SmtDoeDriver</code> : an OpenMDAO driver for sampling methods from surrogate library [SMT](https://smt.readthedocs.io/en/latest/)
* <code>SalibDoeDriver</code> : an OpenMDAO driver for Morris or Saltelli DoE from sensitive anaysis library [SALib](https://salib.readthedocs.io/en/latest/)
* <code>RecklessNonlinearBlockGS</code> : a specialized version of NonlinearBlockGS solver to handle convergence variables specifications.

## Installation
```
pip install openmdao-extensions
```

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

