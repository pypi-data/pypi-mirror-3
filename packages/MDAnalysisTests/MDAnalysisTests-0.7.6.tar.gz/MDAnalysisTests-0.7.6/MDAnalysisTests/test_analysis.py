# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# MDAnalysis --- http://mdanalysis.googlecode.com
# Copyright (c) 2006-2011 Naveen Michaud-Agrawal,
#               Elizabeth J. Denning, Oliver Beckstein,
#               and contributors (see website for details)
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
#     N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and
#     O. Beckstein. MDAnalysis: A Toolkit for the Analysis of
#     Molecular Dynamics Simulations. J. Comput. Chem. 32 (2011), 2319--2327,
#     doi:10.1002/jcc.21787
#

import MDAnalysis
import MDAnalysis.analysis.distances
import MDAnalysis.analysis.align
import MDAnalysis.analysis.hbonds

import numpy as np
from numpy.testing import *
from nose.plugins.attrib import attr

import os
import tempfile

from MDAnalysis.tests.datafiles import PSF,DCD,CRD,FASTA,PDB_helix

class TestContactMatrix(TestCase):
    def setUp(self):
        self.universe = MDAnalysis.Universe(PSF, DCD)
        self.dcd = self.universe.trajectory
        # reasonable precision so that tests succeed on 32 and 64 bit machines
        # (the reference values were obtained on 64 bit)
        # Example:
        #   Items are not equal: wrong maximum distance value
        #   ACTUAL: 52.470254967456412
        #   DESIRED: 52.470257062419059
        self.prec = 5

    def tearDown(self):
        del self.universe
        del self.dcd

    def test_numpy(self):
        U = self.universe
        self.dcd.rewind()
        self.dcd[10]
        # small cutoff value as the input file is a protein
        contacts = MDAnalysis.analysis.distances.contact_matrix(U.atoms.coordinates() , cutoff=1.5 , returntype="numpy")
        assert_equal(contacts.shape, (3341, 3341), "wrong shape (should be (Natoms,Natoms))")
        assert_equal(contacts[0][0] , True , "first entry should be a contact")
        assert_equal(contacts[0][-1] , False , "last entry for first atom should be a non-contact")

    def test_sparse(self):
        U = self.universe
        self.dcd.rewind()
        self.dcd[10]
        # Just taking first 50 atoms as the sparse method is slow
        selection = U.selectAtoms('bynum 1:50')
        # small cutoff value as the input file is a protein
        # High progress_meter_freq so progress meter is not printed during test
        contacts = MDAnalysis.analysis.distances.contact_matrix(selection.coordinates() , cutoff=1.07 , returntype="sparse" , suppress_progmet=True)
        assert_equal(contacts.shape, (50, 50), "wrong shape (should be (50,50))")
        assert_equal(contacts[0,0] , False , "entry (0,0) should be a non-contact")
        assert_equal(contacts[0,2] , True , "entry (0,2) should be a contact")
        assert_equal(contacts[0,3] , True , "entry (0,3) should be a contact")
        assert_equal(contacts[0,4] , False , "entry (0,3) should be a contact")

class TestAlign(TestCase):
    def setUp(self):
        self.universe = MDAnalysis.Universe(PSF, DCD)
        self.reference = MDAnalysis.Universe(PSF, DCD)
        fd, self.outfile = tempfile.mkstemp(suffix=".dcd")  # output is always same as input (=DCD)

    def tearDown(self):
        try:
            os.unlink(self.outfile)
        except OSError:
            pass
        del self.universe
        del self.reference

    def test_rmsd(self):
        self.universe.trajectory[0]      # ensure first frame
        bb = self.universe.selectAtoms('backbone')
        A = bb.coordinates(copy=True)     # coordinates of first frame (copy=True just in case)
        self.universe.trajectory[-1]      # forward to last frame
        B = bb.coordinates()              # coordinates of last frame
        rmsd = MDAnalysis.analysis.align.rmsd(A,B)
        assert_almost_equal(MDAnalysis.analysis.align.rmsd(A,A), 0.0, 5,
                            err_msg="error: rmsd(X,X) should be 0")
        # rmsd(A,B) = rmsd(B,A)  should be exact but spurious failures in the 9th decimal have been
        # observed (see Issue 57 comment #1) so we relax the test to 6 decimals.
        assert_almost_equal(MDAnalysis.analysis.align.rmsd(B,A), rmsd, 6,
                            err_msg="error: rmsd() is not symmetric")
        assert_almost_equal(rmsd, 6.8342494129169804, 5,
                            err_msg="RMSD calculation between 1st and last AdK frame gave wrong answer")

    @dec.slow
    @attr('issue')
    def test_rms_fit_trj(self):
        """Testing align.rms_fit_trj() for all atoms (Issue 58)"""
        # align to *last frame* in target... just for the heck of it
        self.reference.trajectory[-1]
        MDAnalysis.analysis.align.rms_fit_trj(self.universe, self.reference, select="all",
                                              filename=self.outfile)
        fitted = MDAnalysis.Universe(PSF, self.outfile)
        # RMSD against the reference frame
        # calculated on Mac OS X x86 with MDA 0.7.2 r689
        # VMD: 6.9378711
        self._assert_rmsd(fitted, 0, 6.92913674516568)
        self._assert_rmsd(fitted, -1, 0.0)

    def _assert_rmsd(self, fitted, frame, desired):
        fitted.trajectory[frame]
        rmsd = MDAnalysis.analysis.align.rmsd(self.reference.atoms.coordinates(), fitted.atoms.coordinates())
        assert_almost_equal(rmsd, desired, decimal=5,
                            err_msg="frame %d of fit does not have expected RMSD" % frame)

class TestHydrogenBondAnalysis(TestCase):
    def setUp(self):
        self.universe = u = MDAnalysis.Universe(PDB_helix)
        self.detect_hydrogens = "distance"
        # ideal helix with 1 proline:
        self.num_bb_hbonds = u.atoms.numberOfResidues() - u.SYSTEM.PRO.numberOfResidues() - 4

    def _run(self):
        h = MDAnalysis.analysis.hbonds.HydrogenBondAnalysis(self.universe, 'protein', 'protein',
                                                            distance=3.0, angle=150.0, detect_hydrogens=self.detect_hydrogens)
        h.run()
        return h

    def test_helix_backbone(self):
        h = self._run()
        assert_equal(len(h.timeseries[0]), self.num_bb_hbonds, "wrong number of backbone hydrogen bonds")
        assert_equal(h.timesteps, [0.0])

    # TODO: Expand tests because the following ones are a bit superficial
    #       because we should really run them on a trajectory

    def test_count_by_time(self):
        h = self._run()
        c = h.count_by_time()
        assert_equal(c.tolist(), [(0.0, self.num_bb_hbonds)])

    def test_count_by_type(self):
        h = self._run()
        c = h.count_by_type()
        assert_equal(c.frequency, self.num_bb_hbonds * [1.0])

    def test_count_by_type(self):
        h = self._run()
        t = h.timesteps_by_type()
        assert_equal(t.time, self.num_bb_hbonds * [0.0])

    def tearDown(self):
        del self.universe

class TestHydrogenBondAnalysisHeuristic(TestHydrogenBondAnalysis):
    def setUp(self):
        super(TestHydrogenBondAnalysisHeuristic, self).setUp()
        self.detect_hydrogens = "heuristic"

class TestAlignmentProcessing(TestCase):
    def setUp(self):
        self.seq = FASTA
        fd, self.alnfile = tempfile.mkstemp(suffix=".aln")
        fd, self.treefile = tempfile.mkstemp(suffix=".dnd")

    def tearDown(self):
        for f in self.alnfile, self.treefile:
            try:
                os.unlink(f)
            except OSError:
                pass

    @attr('issue')
    def test_fasta2select_aligned(self):
        """test align.fasta2select() on aligned FASTA (Issue 112)"""
        from MDAnalysis.analysis.align import fasta2select
        sel = fasta2select(self.seq, is_aligned=True)
        # length of the output strings, not residues or anything real...
        assert_equal(len(sel['reference']), 30623, err_msg="selection string has unexpected length")
        assert_equal(len(sel['mobile']), 30623, err_msg="selection string has unexpected length")

    @attr('issue')
    def test_fasta2select_ClustalW(self):
        """test align.fasta2select() with calling ClustalW (Issue 113)"""
        # note: will fail if clustalw is not installed
        from MDAnalysis.analysis.align import fasta2select
        sel = fasta2select(self.seq, is_aligned=False, alnfilename=self.alnfile, treefilename=self.treefile)
        # numbers computed from alignment with clustalw 2.1 on Mac OS X [orbeckst]
        # length of the output strings, not residues or anything real...
        assert_equal(len(sel['reference']), 23080, err_msg="selection string has unexpected length")
        assert_equal(len(sel['mobile']), 23090, err_msg="selection string has unexpected length")
