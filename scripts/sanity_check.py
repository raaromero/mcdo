"""Standing sanity harness — the SAME invariants every run.

Run before trusting any result or figure:
    python scripts/sanity_check.py
Exits nonzero if any invariant fails. These are the consistency checks that
catch the classes of error we kept hitting (limits, windows, Linfoot, labels).
Maxwell/Helmholtz first-principles live in audit_first_principles.py (heavier);
this harness is the fast, always-run gate.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
from mcdo import SimConfig, transverse_profile, linfoot_profile
from mcdo.rw_integrals import compute_integrals
from mcdo.annular import compute_integrals_annular
from mcdo.debye import scalar_debye
from mcdo.apodization import gaussian

LAM, N, C = 0.750, 1.3, 2.99792458e14  # match all canonical scripts
AIRY_FWHM_V = 3.2326
fails = []
def check(name, ok, got, tol):
    tag = "PASS" if ok else "FAIL"
    print(f"  [{tag}] {name:52s} {got:>14}  (tol {tol})")
    if not ok:
        fails.append(name)

def fwhm_v(r, I, ksa):
    I = I/I.max(); half=0.5
    below = np.where(I < half)[0]
    if len(below)==0:
        return np.nan
    i=below[0]; r0 = r[i-1]+(r[i]-r[i-1])*(I[i-1]-half)/(I[i-1]-I[i])
    return 2*r0*ksa

print("SANITY HARNESS — specs NA 0.8, lambda 750 nm, n 1.3\n")

# 1-2. Low-NA limits -> Airy (scalar and vector y-cut)
cfg=SimConfig(lam_c=LAM,X_NA=0.1,n=N,tau=np.inf,N_freq=1,N_theta=801)
ksa=cfg.k_c*np.sin(cfg.alpha); r=np.linspace(0,8/ksa,400); z0=np.array([0.0])
Usc=scalar_debye(r,z0,cfg.k_c,cfg.alpha,cfg.N_theta)[0]
I0,I1,I2=compute_integrals(r,z0,cfg.k_c,cfg.alpha,cfg.N_theta)
Ivec=np.abs(I0[0]-I2[0])**2
fsc,fv=fwhm_v(r,Usc,ksa),fwhm_v(r,Ivec,ksa)
check("low-NA scalar FWHM_v -> Airy 3.233", abs(fsc-AIRY_FWHM_V)<0.03, f"{fsc:.3f}", "<0.03")
check("low-NA vector y-cut FWHM_v -> Airy", abs(fv-AIRY_FWHM_V)<0.03, f"{fv:.3f}", "<0.03")

# 3. eps->0 : annular == full disk
cfg=SimConfig(lam_c=LAM,X_NA=0.8,n=N,tau=np.inf,N_freq=1,N_theta=401)
r=np.linspace(0,1.0,120)
full=compute_integrals(r,z0,cfg.k_c,cfg.alpha,cfg.N_theta)[0]
ann =compute_integrals_annular(r,z0,cfg.k_c,cfg.alpha,1e-9,cfg.N_theta)[0]
d=np.max(np.abs(full-ann))
check("eps->0 annular == full disk", d<1e-8, f"{d:.1e}", "<1e-8")

# 4. alpha_t->0 : gaussian == uniform
gu=compute_integrals(r,z0,cfg.k_c,cfg.alpha,cfg.N_theta,apodization=gaussian(0.0,cfg.sin2_alpha))[0]
d=np.max(np.abs(full-gu))
check("alpha_t->0 gaussian == uniform", d<1e-10, f"{d:.1e}", "<1e-10")

# 5. tau->inf : pulsed == CW
cfg=SimConfig(lam_c=LAM,X_NA=0.8,n=N,tau=1e-9,N_freq=11,N_theta=401)
rr=np.linspace(0,1.0,80)
cw=transverse_profile(rr,cfg,pulsed=False); pl=transverse_profile(rr,cfg,pulsed=True)
d=np.max(np.abs(cw/cw.max()-pl/pl.max()))
check("tau->inf pulsed == CW", d<1e-3, f"{d:.1e}", "<1e-3")

# 6. Linfoot identity 2Q - S = F
lf=linfoot_profile(cw, pl)
idt=abs(2*lf['Q']-lf['S']-lf['F'])
check("Linfoot identity 2Q-S=F", idt<1e-9, f"{idt:.1e}", "<1e-9")

# 7. Romallosa reproduction (tau=1fs, NA0.8, transverse window +-6um)
cfg=SimConfig(lam_c=LAM,X_NA=0.8,n=N,tau=1e-15,N_freq=201,N_theta=801)
ksa=cfg.k_c*np.sin(cfg.alpha); mir=lambda h:np.concatenate([h[::-1],h[1:]])
rH=np.linspace(0,6.0,101); zH=np.linspace(0,6.0,101)
St=linfoot_profile(mir(transverse_profile(rH,cfg,False)),mir(transverse_profile(rH,cfg,True)))['S']
check("Romallosa S_tr ~ 1.060 (window +-6um)", abs(St-1.060)<0.010, f"{St:.4f}", "1.060+-0.01")

# 8. coherence length = c*tau  vs Nyquist
coh=C*1.2e-15*1e3
check("coherence c*tau(1.2fs)=359.7 < Nyquist 375", abs(coh-359.7)<1 and coh<375, f"{coh:.1f}", "<375")

# 9. scalar<->vector monotone breakdown (full uniform): dev grows with NA
def dev_scalar_vector(xna):
    c=SimConfig(lam_c=LAM,X_NA=xna,n=N,tau=np.inf,N_freq=1,N_theta=601)
    ks=c.k_c*np.sin(c.alpha); rr=np.linspace(0,6/ks,300)
    fv=fwhm_v(rr,np.abs(compute_integrals(rr,z0,c.k_c,c.alpha,c.N_theta)[0][0]
                        -compute_integrals(rr,z0,c.k_c,c.alpha,c.N_theta)[2][0])**2,ks)
    fs=fwhm_v(rr,scalar_debye(rr,z0,c.k_c,c.alpha,c.N_theta)[0],ks)
    return abs(fv-fs)/fs*100
d01,d08=dev_scalar_vector(0.1),dev_scalar_vector(0.8)
check("scalar<->vector dev grows with NA (0.1<0.8)", d01<d08 and d01<1.0, f"{d01:.2f}<{d08:.2f}%", "monotone")

# ── on axis the three component definitions must coincide (I1 = I2 = 0) ────
from mcdo.components import full as _full, ex_only as _ex, scalar as _sc
c = SimConfig(lam_c=0.750, X_NA=1.2, n=1.3, tau=np.inf, N_freq=3, N_theta=801)
z0 = np.array([0.0]); r0 = np.array([0.0])
J0, J1, J2 = compute_integrals(r0, z0, c.k_c, c.alpha, c.N_theta)
a, b, d = _full(J0[0], J1[0], J2[0])[0], _ex(J0[0], J1[0], J2[0])[0], _sc(J0[0])[0]
spread = max(abs(a - b), abs(a - d)) / a
check("on axis full == Ex only == scalar", spread < 1e-12, f"{spread:.1e}", "<1e-12")

# ── truncating the pupil harder can only widen the focus ──────────────────
c = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=np.inf, N_freq=3, N_theta=801)
ks = c.k_c * c.sin_alpha
rr = np.linspace(0.0, 2.0, 900)
widths = []
for at in [0.0, 1.0, 2.0, 4.0, 8.0]:
    ap = gaussian(at, c.sin2_alpha) if at > 0 else None
    K0, K1, K2 = compute_integrals(rr, z0, c.k_c, c.alpha, c.N_theta, apodization=ap)
    widths.append(fwhm_v(rr, _full(K0[0], K1[0], K2[0]), ks))
mono = all(widths[i] < widths[i + 1] for i in range(len(widths) - 1))
check("focal width grows with truncation coeff", mono,
      f"{widths[0]:.2f}->{widths[-1]:.2f}", "monotone")

# ── in optical coordinates the result cannot depend on wavelength ─────────
def _width_at(lam):
    cc = SimConfig(lam_c=lam, X_NA=0.8, n=1.3, tau=np.inf, N_freq=3, N_theta=801)
    kk = cc.k_c * cc.sin_alpha
    rv = np.linspace(0.0, 12.0 / kk, 900)
    L0, L1, L2 = compute_integrals(rv, z0, cc.k_c, cc.alpha, cc.N_theta)
    return fwhm_v(rv, _full(L0[0], L1[0], L2[0]), kk)
w532, w750 = _width_at(0.532), _width_at(0.750)
check("FWHM_v independent of wavelength", abs(w532 - w750) < 1e-6,
      f"{abs(w532 - w750):.1e}", "<1e-6")

# ── a thin annulus must extend the depth of focus, never shorten it ───────
c = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=np.inf, N_freq=3, N_theta=801)
zz = np.linspace(0.0, 40.0, 3000)
def _dof(eps):
    if eps == 0.0:
        A0, A1, A2 = compute_integrals(r0, zz, c.k_c, c.alpha, c.N_theta)
    else:
        A0, A1, A2 = compute_integrals_annular(r0, zz, c.k_c, c.alpha, eps, c.N_theta)
    I = _full(A0[:, 0], A1[:, 0], A2[:, 0])
    I = I / I.max()
    below = np.where(I < 0.5)[0]
    if not len(below):
        return np.nan
    i = below[0]                      # interpolate, or the grid sets the answer
    return 2 * np.interp(0.5, [I[i], I[i - 1]], [zz[i], zz[i - 1]])
d0, d9 = _dof(0.0), _dof(0.9)
ratio = d9 / d0
check("annular eps=0.9 depth of focus 4.76x (NA 0.8)", abs(ratio - 4.76) < 0.10,
      f"{ratio:.2f}x", "4.76+-0.10")

# The paraxial law 1/(1-eps^2) = 5.26 is the low-aperture limit; the vector
# result falls below it as numerical aperture rises, so the deck must not
# quote the paraxial number at NA 0.8.
check("depth-of-focus gain below paraxial 5.26 at NA 0.8", ratio < 5.26,
      f"{ratio:.2f} < 5.26", "<5.26")


print(f"\n{'ALL SANITY CHECKS PASS' if not fails else 'FAILURES: '+', '.join(fails)}")
sys.exit(1 if fails else 0)
