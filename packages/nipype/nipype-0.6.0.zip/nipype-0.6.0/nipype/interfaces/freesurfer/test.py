'''
Created on 1 May 2012

@author: filo
'''
import nipype.pipeline.engine as pe
from nipype.interfaces.freesurfer.preprocess import ReconAll

r1 = pe.Node(ReconAll(directive="autorecon1"), name="r1")

wf = pe.Workflow(name="wf")

