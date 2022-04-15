#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Adebayo Braimah
# Imaging Research Center
# 
# Copyright 2022 Cincinnati Children's Hospital Medical Center
# 
# TODO: <LICENCSE HERE>
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This :mod: `xfm_tck` package contains modules for the `xfm_tck` tractography pipeline. 
It is split into the following sub-packages:

.. autosummary::

    util
"""
import os
name: str = "xfm_tck"


# # Define constants
# RESOURCEDIR: str = os.path.join(os.path.dirname(__file__), 'resources')
# ATLASDIR: str = os.path.join(RESOURCEDIR,'atlases')
# HTMLDIR: str = os.path.join(RESOURCEDIR,'html')
# GROUP_MAP_DIR: str = os.path.join(RESOURCEDIR,'group_maps')
# GROUP_QC_DIR: str = os.path.join(RESOURCEDIR,'group_qc')
# DEFAULT_SETTINGS_FILE: str = os.path.join(RESOURCEDIR,'settings.default.json')
# DEFAULT_CLASSIFIER: str = os.path.join(RESOURCEDIR,'classifiers','cchmc_neonate_MB3','cchmc_neonate_MB3.RData')
# 
# 
# _version_file: str = os.path.abspath(
#     os.path.join(RESOURCEDIR,'version.txt')
# )
# 
# 
# with open(_version_file,'r') as f:
#     file_contents: str = f.read()
#     _version: str = file_contents.strip("\n")
#     f.close()


__author__          = "Adebayo Braimah"
__credits__         = ["Adebayo Braimah",
                       "Cincinnati Children's Hospital Medical Center", 
                       "Imaging Research Center", 
                       "CCHMC Dept. of Radiology"]
__license__         = "<LICENSE HERE>"
__version__         = '0.0.1' # _version
__maintainer__      = "Adebayo Braimah"
__email__           = "adebayo.braimah@cchmc.org"
__status__          = "Development"