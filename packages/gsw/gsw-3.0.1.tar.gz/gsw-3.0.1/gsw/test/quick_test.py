# Quick value test
import gsw
from gsw.utilities import Dict2Struc

# Read data file with check value profiles
datadir = os.path.join(os.path.dirname(gsw.utilities.__file__), 'data')
cv = Dict2Struc(np.load(os.path.join(datadir, 'gsw_cv_v3_0.npz')))
cf = Dict2Struc(np.load(os.path.join(datadir, 'gsw_cf.npz')))

SA = cv.SA_chck_cast
CT = cv.CT_chck_cast
p = cv.p_chck_cast