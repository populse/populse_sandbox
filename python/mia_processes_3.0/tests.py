from capsul.api import Capsul, Process, Pipeline
from soma.controller import field, File
import typing


class Smooth(Process):
    # Inputs
    in_files: field(type_=File,
                    extensions=('.nii',),
                    optional=False,
                    doc='in_files')
    
    fwhm: field(type_=typing.Union[float, list[float]],
                optional=True,
                doc='fwhm')

    data_type: field(type_=int,
                     optional=True,
                     doc='data_type')

    implicit_masking: field(type_=bool,
                            optional=True,
                            doc='implicit_masking')

    out_prefix: field(type_=str,
                      optional=True,
                      default_factory=lambda: 's',
                      doc='out_prefix')

        # Outputs
    smoothed_files: field(type_=File,
                          write=True,
                          doc='smoothed_files')




if __name__ == '__main__':
    import sys
    from soma.qt_gui.qt_backend import QtGui
    from capsul.qt_gui.widgets import PipelineDeveloperView
    smooth = Capsul.executable('test.Smooth')
    app = QtGui.QApplication.instance()
    if not app:
        app = QtGui.QApplication(sys.argv)
    view1 = PipelineDeveloperView(smooth, allow_open_controller=True, show_sub_pipelines=True)
    view1.show()
    app.exec_()
    del view1

