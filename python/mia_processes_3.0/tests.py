from capsul.api import Capsul, Process, Pipeline
from capsul.qt_gui.widgets import PipelineDeveloperView
from capsul.config.configuration import ApplicationConfiguration

from soma.controller import field, File, Directory
from soma.qt_gui.qt_backend import QtGui

import typing
import sys


class Smooth(Process):

 #   def __init__(self):
  #      self.requirement = ['spm', 'nipype']

    #We can't use types defined by nipype because it use traits ...
    #from nipype.interfaces.base import (File, InputMultiPath, InputMultiObject,
    #                                    OutputMultiPath, traits,
    #                                    TraitListObject,
    #                                    traits_extension)
    #from nipype.interfaces.spm.base import ImageFileSPM

    #in_files: InputMultiPath[ImageFileSPM] = field(extensions='.nii',
    #                                               optional=False,
    #                                               doc='in_files')
    # Inputs
    in_files: typing.Union[list[File], File] = field(extensions='.nii',
    #in_files: File = field(extensions='.nii',
                           optional=False,
                           doc='in_files description')

    fwhm: typing.Union[float, list[float]] = field(optional=True,
                                                   default_factory=lambda: [6., 6., 6.],
                                                   doc='fwhm description')

    data_type: int = field(default_factory=lambda: 0,
                           optional=True,
                           doc='data_type')

    implicit_masking: bool = field(optional=True,
                                   default_factory=lambda: False,
                                   doc='implicit_masking description')

    out_prefix: str = field(optional=True,
                            default_factory=lambda: 's',
                            doc='out_prefix description')


    output_directory: Directory = field(optional=False,
                                        userlevel=1,
                                        #default_factory=lambda: 's',
                                        #doc='out_prefix description')
                                        )
    # Outputs
    smoothed_files: File = field(write=True,
                                 doc='smoothed_files description')

    capsul = Capsul()
    process = capsul.executable('nipype.interfaces.spm.preprocess.Smooth')

    def execute(self, context):
        # with open(self.input) as f:
        #     content = f.read()
        # content = f'{content}Bias correction with strength={self.strength}\n'
        # Path(self.output).parent.mkdir(parents=True, exist_ok=True)
        # with open(self.output, 'w') as f:
        #     f.write(content)
        # print('self.in_files: ', self.in_files)
        # print('self.fwhm: ', self.fwhm)
        # print('self.data_type: ', self.data_type)
        # print('self.implicit_masking: ', self.implicit_masking)
        # print('self.out_prefix: ', self.out_prefix)
        self.process.in_files = self.in_files
        self.process.fwhm= self.fwhm
        self.process.data_type = self.data_type
        self.process.implicit_masking = self.implicit_masking
        self.process.out_prefix = self.out_prefix
        self.process.output_directory = self.output_directory

        #print('self.smoothed_files: ', self.smoothed_files)
        #print('self.process: ', self.process)
        self.process.execute(context=None)

if __name__ == '__main__':
    app = QtGui.QApplication.instance()

    capsul = Capsul()
    smooth = capsul.executable('tests.Smooth')

    config = ApplicationConfiguration('test_smoothV3')
    user_conf_dict = {
        'local': {
            'spm': {
                'spm12_standalone': {
                    'directory': '/usr/local/SPM/spm12_standalone',
                    'standalone': True,
                    'version': 12},
                    },
            'nipype': {
                'nipype': {}
                      },
            'matlab': {
                'matlab': {
                    'mcr_directory': '/usr/local/MATLAB/MATLAB_Runtime/v95 '}
                      }
                  }
                }

    config.user = user_conf_dict
    config.merge_configs()
    capsul.config = config.merged_config
    print('local config: ', capsul.config.asdict())

    smooth.in_files = ['/home/econdami/Desktop/Data_tests_capsulV3/raw/alej170316-IRM_Fonct._+_perfusion-2016-03-17_08-34-44-1-T1_3D_SENSE-T1TFE-00-04-25.000.nii']
    smooth.output_directory = '/home/econdami/Desktop/Data_tests_capsulV3/derived'


    #c.engine().config.local ######  pas bon
    #c.config.local= un dict ou un controller
    #https://github.com/populse/capsul/blob/pydantic_controller/capsul/config/test/test_config.py
    if not app:
        app = QtGui.QApplication(sys.argv)
        
    view1 = PipelineDeveloperView(smooth, allow_open_controller=True, show_sub_pipelines=True)
    
    view1.show()
    app.exec_()
    del view1

    
    with capsul.engine() as engine:
        engine.run(smooth)
    
    #print('smooth.asdict(): ', smooth.asdict())
