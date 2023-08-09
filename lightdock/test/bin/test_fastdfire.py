"""Regression tests for testing C DFIRE scoring function"""

import shutil
import os
import filecmp
from pathlib import Path


class TestRegressionFastDFIREShort:
    def setup_class(self):
        self.path = Path(__file__).absolute().parent
        self.golden_data_path = self.path / "golden_data" / "regression_fastdfire_short"

    def test_lightdock_2uuy_5_steps_25_glowworms_100_swarms(self, tmp_path):
        os.chdir(tmp_path)
        shutil.copy(self.golden_data_path / "2UUY_rec.pdb", tmp_path)
        shutil.copy(self.golden_data_path / "2UUY_lig.pdb", tmp_path)

        num_swarms = 100
        num_glowworms = 25
        steps = 5

        command = f"lightdock3_setup.py 2UUY_rec.pdb 2UUY_lig.pdb -g {num_glowworms} -s {num_swarms} -anm"
        command += ">> test_lightdock.out"
        os.system(command)

        command = f"lightdock3.py -c 1 -s fastdfire setup.json {steps} -l 10 >> test_lightdock.out"
        os.system(command)

        assert filecmp.cmp(
            self.golden_data_path / "swarm_10" / "gso_0.out",
            tmp_path / "swarm_10" / "gso_0.out",
        )
        assert (tmp_path / "swarm_10" / "gso_5.out").exists()


class TestRegressionFastDFIRERestraints:
    def setup_class(self):
        self.path = Path(__file__).absolute().parent
        self.golden_data_path = self.path / "golden_data" / "regression_fastdfire_restraints"

    def test_lightdock_2uuy_5_steps_25_glowworms_rst(self, tmp_path):
        os.chdir(tmp_path)
        shutil.copy(self.golden_data_path / "2UUY_rec.pdb", tmp_path)
        shutil.copy(self.golden_data_path / "2UUY_lig.pdb", tmp_path)
        shutil.copy(self.golden_data_path / "restraints.list", tmp_path)

        num_glowworms = 25
        steps = 5

        command = (
            f"lightdock3_setup.py 2UUY_rec.pdb 2UUY_lig.pdb -g {num_glowworms} -anm "
        )
        command += "-rst restraints.list >> test_lightdock.out"
        os.system(command)

        command = f"lightdock3.py -c 1 -s fastdfire setup.json {steps} -l 0 >> test_lightdock.out"
        os.system(command)

        assert filecmp.cmp(
            self.golden_data_path / "swarm_0" / "gso_0.out",
            tmp_path / "swarm_0" / "gso_0.out",
        )
        assert (tmp_path / "swarm_0" / "gso_5.out").exists()


class TestRegressionFastDFIRELong:
    def setup_class(self):
        self.path = Path(__file__).absolute().parent
        self.golden_data_path = self.path / "golden_data" / "regression_fastdfire_long"

    def test_lightdock_2uuy_40_steps_50_glowworms(self, tmp_path):
        os.chdir(tmp_path)
        shutil.copy(self.golden_data_path / "2UUY_rec.pdb", tmp_path)
        shutil.copy(self.golden_data_path / "2UUY_lig.pdb", tmp_path)

        num_glowworms = 50
        steps = 40

        command = f"lightdock3_setup.py 2UUY_rec.pdb 2UUY_lig.pdb -g {num_glowworms} >> test_lightdock.out"
        os.system(command)

        command = f"lightdock3.py -c 1 -s fastdfire setup.json {steps} -l 100 >> test_lightdock.out"
        os.system(command)

        assert filecmp.cmp(
            self.golden_data_path / "swarm_100" / "gso_0.out",
            tmp_path / "swarm_100" / "gso_0.out",
        )
        assert filecmp.cmp(
            self.golden_data_path / "init" / "swarm_centers.pdb",
            tmp_path / "init" / "swarm_centers.pdb",
        )
        assert (tmp_path / "swarm_100" / "gso_10.out").exists()
        assert (tmp_path / "swarm_100" / "gso_20.out").exists()
        assert (tmp_path / "swarm_100" / "gso_30.out").exists()
        assert (tmp_path / "swarm_100" / "gso_40.out").exists()


class TestRegressionFastDFIRELocalMinimization:
    def setup_class(self):
        self.path = Path(__file__).absolute().parent
        self.golden_data_path = self.path / "golden_data" / "regression_fastdfire_min"

    def test_lightdock_2uuy_2_steps_local_min(self, tmp_path):
        os.chdir(tmp_path)
        shutil.copy(self.golden_data_path / "2UUY_rec.pdb", tmp_path)
        shutil.copy(self.golden_data_path / "2UUY_lig.pdb", tmp_path)

        steps = 10
        swarm = 0

        command = "lightdock3_setup.py 2UUY_rec.pdb 2UUY_lig.pdb --noh --now --noxt -anm >> test_lightdock.out"
        os.system(command)

        command = f"lightdock3.py -c 1 -s fastdfire setup.json {steps} -l {swarm} -min >> test_lightdock.out"
        os.system(command)

        assert filecmp.cmp(
            self.golden_data_path / "swarm_0" / "gso_0.out",
            tmp_path / "swarm_0" / "gso_0.out",
        )
        assert (tmp_path / "swarm_0" / "gso_10.out").exists()
