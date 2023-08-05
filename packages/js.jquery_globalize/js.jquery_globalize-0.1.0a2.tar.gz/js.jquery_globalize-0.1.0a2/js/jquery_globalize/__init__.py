import fanstatic
import js.jquery

library = fanstatic.Library('jquery_globalize', 'resources')

globalize = fanstatic.Resource(
    library, 'globalize.js', depends=[js.jquery.jquery])

cultures = fanstatic.Resource(
    library, 'cultures/globalize.cultures.js', depends=[globalize])

# Auto-generated:
#
# template = '''
# culture_%s = fanstatic.Resource(
#     library, 'cultures/globalize.culture.%s', depends=[globalize])'''
#
# for locale in [
#     'af-ZA.js',
#     ...
#     'zu.js']:
#     print template % (''.join(locale.split('.')[:-1]).lower().replace('-', '_'), locale)

culture_af_za = fanstatic.Resource(
    library, 'cultures/globalize.culture.af-ZA.js', depends=[globalize])

culture_af = fanstatic.Resource(
    library, 'cultures/globalize.culture.af.js', depends=[globalize])

culture_am_et = fanstatic.Resource(
    library, 'cultures/globalize.culture.am-ET.js', depends=[globalize])

culture_am = fanstatic.Resource(
    library, 'cultures/globalize.culture.am.js', depends=[globalize])

culture_ar_ae = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-AE.js', depends=[globalize])

culture_ar_bh = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-BH.js', depends=[globalize])

culture_ar_dz = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-DZ.js', depends=[globalize])

culture_ar_eg = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-EG.js', depends=[globalize])

culture_ar_iq = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-IQ.js', depends=[globalize])

culture_ar_jo = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-JO.js', depends=[globalize])

culture_ar_kw = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-KW.js', depends=[globalize])

culture_ar_lb = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-LB.js', depends=[globalize])

culture_ar_ly = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-LY.js', depends=[globalize])

culture_ar_ma = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-MA.js', depends=[globalize])

culture_ar_om = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-OM.js', depends=[globalize])

culture_ar_qa = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-QA.js', depends=[globalize])

culture_ar_sa = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-SA.js', depends=[globalize])

culture_ar_sy = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-SY.js', depends=[globalize])

culture_ar_tn = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-TN.js', depends=[globalize])

culture_ar_ye = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar-YE.js', depends=[globalize])

culture_ar = fanstatic.Resource(
    library, 'cultures/globalize.culture.ar.js', depends=[globalize])

culture_arn_cl = fanstatic.Resource(
    library, 'cultures/globalize.culture.arn-CL.js', depends=[globalize])

culture_arn = fanstatic.Resource(
    library, 'cultures/globalize.culture.arn.js', depends=[globalize])

culture_as_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.as-IN.js', depends=[globalize])

culture_as = fanstatic.Resource(
    library, 'cultures/globalize.culture.as.js', depends=[globalize])

culture_az_cyrl_az = fanstatic.Resource(
    library, 'cultures/globalize.culture.az-Cyrl-AZ.js', depends=[globalize])

culture_az_cyrl = fanstatic.Resource(
    library, 'cultures/globalize.culture.az-Cyrl.js', depends=[globalize])

culture_az_latn_az = fanstatic.Resource(
    library, 'cultures/globalize.culture.az-Latn-AZ.js', depends=[globalize])

culture_az_latn = fanstatic.Resource(
    library, 'cultures/globalize.culture.az-Latn.js', depends=[globalize])

culture_az = fanstatic.Resource(
    library, 'cultures/globalize.culture.az.js', depends=[globalize])

culture_ba_ru = fanstatic.Resource(
    library, 'cultures/globalize.culture.ba-RU.js', depends=[globalize])

culture_ba = fanstatic.Resource(
    library, 'cultures/globalize.culture.ba.js', depends=[globalize])

culture_be_by = fanstatic.Resource(
    library, 'cultures/globalize.culture.be-BY.js', depends=[globalize])

culture_be = fanstatic.Resource(
    library, 'cultures/globalize.culture.be.js', depends=[globalize])

culture_bg_bg = fanstatic.Resource(
    library, 'cultures/globalize.culture.bg-BG.js', depends=[globalize])

culture_bg = fanstatic.Resource(
    library, 'cultures/globalize.culture.bg.js', depends=[globalize])

culture_bn_bd = fanstatic.Resource(
    library, 'cultures/globalize.culture.bn-BD.js', depends=[globalize])

culture_bn_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.bn-IN.js', depends=[globalize])

culture_bn = fanstatic.Resource(
    library, 'cultures/globalize.culture.bn.js', depends=[globalize])

culture_bo_cn = fanstatic.Resource(
    library, 'cultures/globalize.culture.bo-CN.js', depends=[globalize])

culture_bo = fanstatic.Resource(
    library, 'cultures/globalize.culture.bo.js', depends=[globalize])

culture_br_fr = fanstatic.Resource(
    library, 'cultures/globalize.culture.br-FR.js', depends=[globalize])

culture_br = fanstatic.Resource(
    library, 'cultures/globalize.culture.br.js', depends=[globalize])

culture_bs_cyrl_ba = fanstatic.Resource(
    library, 'cultures/globalize.culture.bs-Cyrl-BA.js', depends=[globalize])

culture_bs_cyrl = fanstatic.Resource(
    library, 'cultures/globalize.culture.bs-Cyrl.js', depends=[globalize])

culture_bs_latn_ba = fanstatic.Resource(
    library, 'cultures/globalize.culture.bs-Latn-BA.js', depends=[globalize])

culture_bs_latn = fanstatic.Resource(
    library, 'cultures/globalize.culture.bs-Latn.js', depends=[globalize])

culture_bs = fanstatic.Resource(
    library, 'cultures/globalize.culture.bs.js', depends=[globalize])

culture_ca_es = fanstatic.Resource(
    library, 'cultures/globalize.culture.ca-ES.js', depends=[globalize])

culture_ca = fanstatic.Resource(
    library, 'cultures/globalize.culture.ca.js', depends=[globalize])

culture_co_fr = fanstatic.Resource(
    library, 'cultures/globalize.culture.co-FR.js', depends=[globalize])

culture_co = fanstatic.Resource(
    library, 'cultures/globalize.culture.co.js', depends=[globalize])

culture_cs_cz = fanstatic.Resource(
    library, 'cultures/globalize.culture.cs-CZ.js', depends=[globalize])

culture_cs = fanstatic.Resource(
    library, 'cultures/globalize.culture.cs.js', depends=[globalize])

culture_cy_gb = fanstatic.Resource(
    library, 'cultures/globalize.culture.cy-GB.js', depends=[globalize])

culture_cy = fanstatic.Resource(
    library, 'cultures/globalize.culture.cy.js', depends=[globalize])

culture_da_dk = fanstatic.Resource(
    library, 'cultures/globalize.culture.da-DK.js', depends=[globalize])

culture_da = fanstatic.Resource(
    library, 'cultures/globalize.culture.da.js', depends=[globalize])

culture_de_at = fanstatic.Resource(
    library, 'cultures/globalize.culture.de-AT.js', depends=[globalize])

culture_de_ch = fanstatic.Resource(
    library, 'cultures/globalize.culture.de-CH.js', depends=[globalize])

culture_de_de = fanstatic.Resource(
    library, 'cultures/globalize.culture.de-DE.js', depends=[globalize])

culture_de_li = fanstatic.Resource(
    library, 'cultures/globalize.culture.de-LI.js', depends=[globalize])

culture_de_lu = fanstatic.Resource(
    library, 'cultures/globalize.culture.de-LU.js', depends=[globalize])

culture_de = fanstatic.Resource(
    library, 'cultures/globalize.culture.de.js', depends=[globalize])

culture_dsb_de = fanstatic.Resource(
    library, 'cultures/globalize.culture.dsb-DE.js', depends=[globalize])

culture_dsb = fanstatic.Resource(
    library, 'cultures/globalize.culture.dsb.js', depends=[globalize])

culture_dv_mv = fanstatic.Resource(
    library, 'cultures/globalize.culture.dv-MV.js', depends=[globalize])

culture_dv = fanstatic.Resource(
    library, 'cultures/globalize.culture.dv.js', depends=[globalize])

culture_el_gr = fanstatic.Resource(
    library, 'cultures/globalize.culture.el-GR.js', depends=[globalize])

culture_el = fanstatic.Resource(
    library, 'cultures/globalize.culture.el.js', depends=[globalize])

culture_en_029 = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-029.js', depends=[globalize])

culture_en_au = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-AU.js', depends=[globalize])

culture_en_bz = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-BZ.js', depends=[globalize])

culture_en_ca = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-CA.js', depends=[globalize])

culture_en_gb = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-GB.js', depends=[globalize])

culture_en_ie = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-IE.js', depends=[globalize])

culture_en_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-IN.js', depends=[globalize])

culture_en_jm = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-JM.js', depends=[globalize])

culture_en_my = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-MY.js', depends=[globalize])

culture_en_nz = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-NZ.js', depends=[globalize])

culture_en_ph = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-PH.js', depends=[globalize])

culture_en_sg = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-SG.js', depends=[globalize])

culture_en_tt = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-TT.js', depends=[globalize])

culture_en_us = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-US.js', depends=[globalize])

culture_en_za = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-ZA.js', depends=[globalize])

culture_en_zw = fanstatic.Resource(
    library, 'cultures/globalize.culture.en-ZW.js', depends=[globalize])

culture_es_ar = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-AR.js', depends=[globalize])

culture_es_bo = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-BO.js', depends=[globalize])

culture_es_cl = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-CL.js', depends=[globalize])

culture_es_co = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-CO.js', depends=[globalize])

culture_es_cr = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-CR.js', depends=[globalize])

culture_es_do = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-DO.js', depends=[globalize])

culture_es_ec = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-EC.js', depends=[globalize])

culture_es_es = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-ES.js', depends=[globalize])

culture_es_gt = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-GT.js', depends=[globalize])

culture_es_hn = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-HN.js', depends=[globalize])

culture_es_mx = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-MX.js', depends=[globalize])

culture_es_ni = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-NI.js', depends=[globalize])

culture_es_pa = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-PA.js', depends=[globalize])

culture_es_pe = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-PE.js', depends=[globalize])

culture_es_pr = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-PR.js', depends=[globalize])

culture_es_py = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-PY.js', depends=[globalize])

culture_es_sv = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-SV.js', depends=[globalize])

culture_es_us = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-US.js', depends=[globalize])

culture_es_uy = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-UY.js', depends=[globalize])

culture_es_ve = fanstatic.Resource(
    library, 'cultures/globalize.culture.es-VE.js', depends=[globalize])

culture_es = fanstatic.Resource(
    library, 'cultures/globalize.culture.es.js', depends=[globalize])

culture_et_ee = fanstatic.Resource(
    library, 'cultures/globalize.culture.et-EE.js', depends=[globalize])

culture_et = fanstatic.Resource(
    library, 'cultures/globalize.culture.et.js', depends=[globalize])

culture_eu_es = fanstatic.Resource(
    library, 'cultures/globalize.culture.eu-ES.js', depends=[globalize])

culture_eu = fanstatic.Resource(
    library, 'cultures/globalize.culture.eu.js', depends=[globalize])

culture_fa_ir = fanstatic.Resource(
    library, 'cultures/globalize.culture.fa-IR.js', depends=[globalize])

culture_fa = fanstatic.Resource(
    library, 'cultures/globalize.culture.fa.js', depends=[globalize])

culture_fi_fi = fanstatic.Resource(
    library, 'cultures/globalize.culture.fi-FI.js', depends=[globalize])

culture_fi = fanstatic.Resource(
    library, 'cultures/globalize.culture.fi.js', depends=[globalize])

culture_fil_ph = fanstatic.Resource(
    library, 'cultures/globalize.culture.fil-PH.js', depends=[globalize])

culture_fil = fanstatic.Resource(
    library, 'cultures/globalize.culture.fil.js', depends=[globalize])

culture_fo_fo = fanstatic.Resource(
    library, 'cultures/globalize.culture.fo-FO.js', depends=[globalize])

culture_fo = fanstatic.Resource(
    library, 'cultures/globalize.culture.fo.js', depends=[globalize])

culture_fr_be = fanstatic.Resource(
    library, 'cultures/globalize.culture.fr-BE.js', depends=[globalize])

culture_fr_ca = fanstatic.Resource(
    library, 'cultures/globalize.culture.fr-CA.js', depends=[globalize])

culture_fr_ch = fanstatic.Resource(
    library, 'cultures/globalize.culture.fr-CH.js', depends=[globalize])

culture_fr_fr = fanstatic.Resource(
    library, 'cultures/globalize.culture.fr-FR.js', depends=[globalize])

culture_fr_lu = fanstatic.Resource(
    library, 'cultures/globalize.culture.fr-LU.js', depends=[globalize])

culture_fr_mc = fanstatic.Resource(
    library, 'cultures/globalize.culture.fr-MC.js', depends=[globalize])

culture_fr = fanstatic.Resource(
    library, 'cultures/globalize.culture.fr.js', depends=[globalize])

culture_fy_nl = fanstatic.Resource(
    library, 'cultures/globalize.culture.fy-NL.js', depends=[globalize])

culture_fy = fanstatic.Resource(
    library, 'cultures/globalize.culture.fy.js', depends=[globalize])

culture_ga_ie = fanstatic.Resource(
    library, 'cultures/globalize.culture.ga-IE.js', depends=[globalize])

culture_ga = fanstatic.Resource(
    library, 'cultures/globalize.culture.ga.js', depends=[globalize])

culture_gd_gb = fanstatic.Resource(
    library, 'cultures/globalize.culture.gd-GB.js', depends=[globalize])

culture_gd = fanstatic.Resource(
    library, 'cultures/globalize.culture.gd.js', depends=[globalize])

culture_gl_es = fanstatic.Resource(
    library, 'cultures/globalize.culture.gl-ES.js', depends=[globalize])

culture_gl = fanstatic.Resource(
    library, 'cultures/globalize.culture.gl.js', depends=[globalize])

culture_gsw_fr = fanstatic.Resource(
    library, 'cultures/globalize.culture.gsw-FR.js', depends=[globalize])

culture_gsw = fanstatic.Resource(
    library, 'cultures/globalize.culture.gsw.js', depends=[globalize])

culture_gu_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.gu-IN.js', depends=[globalize])

culture_gu = fanstatic.Resource(
    library, 'cultures/globalize.culture.gu.js', depends=[globalize])

culture_ha_latn_ng = fanstatic.Resource(
    library, 'cultures/globalize.culture.ha-Latn-NG.js', depends=[globalize])

culture_ha_latn = fanstatic.Resource(
    library, 'cultures/globalize.culture.ha-Latn.js', depends=[globalize])

culture_ha = fanstatic.Resource(
    library, 'cultures/globalize.culture.ha.js', depends=[globalize])

culture_he_il = fanstatic.Resource(
    library, 'cultures/globalize.culture.he-IL.js', depends=[globalize])

culture_he = fanstatic.Resource(
    library, 'cultures/globalize.culture.he.js', depends=[globalize])

culture_hi_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.hi-IN.js', depends=[globalize])

culture_hi = fanstatic.Resource(
    library, 'cultures/globalize.culture.hi.js', depends=[globalize])

culture_hr_ba = fanstatic.Resource(
    library, 'cultures/globalize.culture.hr-BA.js', depends=[globalize])

culture_hr_hr = fanstatic.Resource(
    library, 'cultures/globalize.culture.hr-HR.js', depends=[globalize])

culture_hr = fanstatic.Resource(
    library, 'cultures/globalize.culture.hr.js', depends=[globalize])

culture_hsb_de = fanstatic.Resource(
    library, 'cultures/globalize.culture.hsb-DE.js', depends=[globalize])

culture_hsb = fanstatic.Resource(
    library, 'cultures/globalize.culture.hsb.js', depends=[globalize])

culture_hu_hu = fanstatic.Resource(
    library, 'cultures/globalize.culture.hu-HU.js', depends=[globalize])

culture_hu = fanstatic.Resource(
    library, 'cultures/globalize.culture.hu.js', depends=[globalize])

culture_hy_am = fanstatic.Resource(
    library, 'cultures/globalize.culture.hy-AM.js', depends=[globalize])

culture_hy = fanstatic.Resource(
    library, 'cultures/globalize.culture.hy.js', depends=[globalize])

culture_id_id = fanstatic.Resource(
    library, 'cultures/globalize.culture.id-ID.js', depends=[globalize])

culture_id = fanstatic.Resource(
    library, 'cultures/globalize.culture.id.js', depends=[globalize])

culture_ig_ng = fanstatic.Resource(
    library, 'cultures/globalize.culture.ig-NG.js', depends=[globalize])

culture_ig = fanstatic.Resource(
    library, 'cultures/globalize.culture.ig.js', depends=[globalize])

culture_ii_cn = fanstatic.Resource(
    library, 'cultures/globalize.culture.ii-CN.js', depends=[globalize])

culture_ii = fanstatic.Resource(
    library, 'cultures/globalize.culture.ii.js', depends=[globalize])

culture_is_is = fanstatic.Resource(
    library, 'cultures/globalize.culture.is-IS.js', depends=[globalize])

culture_is = fanstatic.Resource(
    library, 'cultures/globalize.culture.is.js', depends=[globalize])

culture_it_ch = fanstatic.Resource(
    library, 'cultures/globalize.culture.it-CH.js', depends=[globalize])

culture_it_it = fanstatic.Resource(
    library, 'cultures/globalize.culture.it-IT.js', depends=[globalize])

culture_it = fanstatic.Resource(
    library, 'cultures/globalize.culture.it.js', depends=[globalize])

culture_iu_cans_ca = fanstatic.Resource(
    library, 'cultures/globalize.culture.iu-Cans-CA.js', depends=[globalize])

culture_iu_cans = fanstatic.Resource(
    library, 'cultures/globalize.culture.iu-Cans.js', depends=[globalize])

culture_iu_latn_ca = fanstatic.Resource(
    library, 'cultures/globalize.culture.iu-Latn-CA.js', depends=[globalize])

culture_iu_latn = fanstatic.Resource(
    library, 'cultures/globalize.culture.iu-Latn.js', depends=[globalize])

culture_iu = fanstatic.Resource(
    library, 'cultures/globalize.culture.iu.js', depends=[globalize])

culture_ja_jp = fanstatic.Resource(
    library, 'cultures/globalize.culture.ja-JP.js', depends=[globalize])

culture_ja = fanstatic.Resource(
    library, 'cultures/globalize.culture.ja.js', depends=[globalize])

culture_ka_ge = fanstatic.Resource(
    library, 'cultures/globalize.culture.ka-GE.js', depends=[globalize])

culture_ka = fanstatic.Resource(
    library, 'cultures/globalize.culture.ka.js', depends=[globalize])

culture_kk_kz = fanstatic.Resource(
    library, 'cultures/globalize.culture.kk-KZ.js', depends=[globalize])

culture_kk = fanstatic.Resource(
    library, 'cultures/globalize.culture.kk.js', depends=[globalize])

culture_kl_gl = fanstatic.Resource(
    library, 'cultures/globalize.culture.kl-GL.js', depends=[globalize])

culture_kl = fanstatic.Resource(
    library, 'cultures/globalize.culture.kl.js', depends=[globalize])

culture_km_kh = fanstatic.Resource(
    library, 'cultures/globalize.culture.km-KH.js', depends=[globalize])

culture_km = fanstatic.Resource(
    library, 'cultures/globalize.culture.km.js', depends=[globalize])

culture_kn_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.kn-IN.js', depends=[globalize])

culture_kn = fanstatic.Resource(
    library, 'cultures/globalize.culture.kn.js', depends=[globalize])

culture_ko_kr = fanstatic.Resource(
    library, 'cultures/globalize.culture.ko-KR.js', depends=[globalize])

culture_ko = fanstatic.Resource(
    library, 'cultures/globalize.culture.ko.js', depends=[globalize])

culture_kok_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.kok-IN.js', depends=[globalize])

culture_kok = fanstatic.Resource(
    library, 'cultures/globalize.culture.kok.js', depends=[globalize])

culture_ky_kg = fanstatic.Resource(
    library, 'cultures/globalize.culture.ky-KG.js', depends=[globalize])

culture_ky = fanstatic.Resource(
    library, 'cultures/globalize.culture.ky.js', depends=[globalize])

culture_lb_lu = fanstatic.Resource(
    library, 'cultures/globalize.culture.lb-LU.js', depends=[globalize])

culture_lb = fanstatic.Resource(
    library, 'cultures/globalize.culture.lb.js', depends=[globalize])

culture_lo_la = fanstatic.Resource(
    library, 'cultures/globalize.culture.lo-LA.js', depends=[globalize])

culture_lo = fanstatic.Resource(
    library, 'cultures/globalize.culture.lo.js', depends=[globalize])

culture_lt_lt = fanstatic.Resource(
    library, 'cultures/globalize.culture.lt-LT.js', depends=[globalize])

culture_lt = fanstatic.Resource(
    library, 'cultures/globalize.culture.lt.js', depends=[globalize])

culture_lv_lv = fanstatic.Resource(
    library, 'cultures/globalize.culture.lv-LV.js', depends=[globalize])

culture_lv = fanstatic.Resource(
    library, 'cultures/globalize.culture.lv.js', depends=[globalize])

culture_mi_nz = fanstatic.Resource(
    library, 'cultures/globalize.culture.mi-NZ.js', depends=[globalize])

culture_mi = fanstatic.Resource(
    library, 'cultures/globalize.culture.mi.js', depends=[globalize])

culture_mk_mk = fanstatic.Resource(
    library, 'cultures/globalize.culture.mk-MK.js', depends=[globalize])

culture_mk = fanstatic.Resource(
    library, 'cultures/globalize.culture.mk.js', depends=[globalize])

culture_ml_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.ml-IN.js', depends=[globalize])

culture_ml = fanstatic.Resource(
    library, 'cultures/globalize.culture.ml.js', depends=[globalize])

culture_mn_cyrl = fanstatic.Resource(
    library, 'cultures/globalize.culture.mn-Cyrl.js', depends=[globalize])

culture_mn_mn = fanstatic.Resource(
    library, 'cultures/globalize.culture.mn-MN.js', depends=[globalize])

culture_mn_mong_cn = fanstatic.Resource(
    library, 'cultures/globalize.culture.mn-Mong-CN.js', depends=[globalize])

culture_mn_mong = fanstatic.Resource(
    library, 'cultures/globalize.culture.mn-Mong.js', depends=[globalize])

culture_mn = fanstatic.Resource(
    library, 'cultures/globalize.culture.mn.js', depends=[globalize])

culture_moh_ca = fanstatic.Resource(
    library, 'cultures/globalize.culture.moh-CA.js', depends=[globalize])

culture_moh = fanstatic.Resource(
    library, 'cultures/globalize.culture.moh.js', depends=[globalize])

culture_mr_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.mr-IN.js', depends=[globalize])

culture_mr = fanstatic.Resource(
    library, 'cultures/globalize.culture.mr.js', depends=[globalize])

culture_ms_bn = fanstatic.Resource(
    library, 'cultures/globalize.culture.ms-BN.js', depends=[globalize])

culture_ms_my = fanstatic.Resource(
    library, 'cultures/globalize.culture.ms-MY.js', depends=[globalize])

culture_ms = fanstatic.Resource(
    library, 'cultures/globalize.culture.ms.js', depends=[globalize])

culture_mt_mt = fanstatic.Resource(
    library, 'cultures/globalize.culture.mt-MT.js', depends=[globalize])

culture_mt = fanstatic.Resource(
    library, 'cultures/globalize.culture.mt.js', depends=[globalize])

culture_nb_no = fanstatic.Resource(
    library, 'cultures/globalize.culture.nb-NO.js', depends=[globalize])

culture_nb = fanstatic.Resource(
    library, 'cultures/globalize.culture.nb.js', depends=[globalize])

culture_ne_np = fanstatic.Resource(
    library, 'cultures/globalize.culture.ne-NP.js', depends=[globalize])

culture_ne = fanstatic.Resource(
    library, 'cultures/globalize.culture.ne.js', depends=[globalize])

culture_nl_be = fanstatic.Resource(
    library, 'cultures/globalize.culture.nl-BE.js', depends=[globalize])

culture_nl_nl = fanstatic.Resource(
    library, 'cultures/globalize.culture.nl-NL.js', depends=[globalize])

culture_nl = fanstatic.Resource(
    library, 'cultures/globalize.culture.nl.js', depends=[globalize])

culture_nn_no = fanstatic.Resource(
    library, 'cultures/globalize.culture.nn-NO.js', depends=[globalize])

culture_nn = fanstatic.Resource(
    library, 'cultures/globalize.culture.nn.js', depends=[globalize])

culture_no = fanstatic.Resource(
    library, 'cultures/globalize.culture.no.js', depends=[globalize])

culture_nso_za = fanstatic.Resource(
    library, 'cultures/globalize.culture.nso-ZA.js', depends=[globalize])

culture_nso = fanstatic.Resource(
    library, 'cultures/globalize.culture.nso.js', depends=[globalize])

culture_oc_fr = fanstatic.Resource(
    library, 'cultures/globalize.culture.oc-FR.js', depends=[globalize])

culture_oc = fanstatic.Resource(
    library, 'cultures/globalize.culture.oc.js', depends=[globalize])

culture_or_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.or-IN.js', depends=[globalize])

culture_or = fanstatic.Resource(
    library, 'cultures/globalize.culture.or.js', depends=[globalize])

culture_pa_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.pa-IN.js', depends=[globalize])

culture_pa = fanstatic.Resource(
    library, 'cultures/globalize.culture.pa.js', depends=[globalize])

culture_pl_pl = fanstatic.Resource(
    library, 'cultures/globalize.culture.pl-PL.js', depends=[globalize])

culture_pl = fanstatic.Resource(
    library, 'cultures/globalize.culture.pl.js', depends=[globalize])

culture_prs_af = fanstatic.Resource(
    library, 'cultures/globalize.culture.prs-AF.js', depends=[globalize])

culture_prs = fanstatic.Resource(
    library, 'cultures/globalize.culture.prs.js', depends=[globalize])

culture_ps_af = fanstatic.Resource(
    library, 'cultures/globalize.culture.ps-AF.js', depends=[globalize])

culture_ps = fanstatic.Resource(
    library, 'cultures/globalize.culture.ps.js', depends=[globalize])

culture_pt_br = fanstatic.Resource(
    library, 'cultures/globalize.culture.pt-BR.js', depends=[globalize])

culture_pt_pt = fanstatic.Resource(
    library, 'cultures/globalize.culture.pt-PT.js', depends=[globalize])

culture_pt = fanstatic.Resource(
    library, 'cultures/globalize.culture.pt.js', depends=[globalize])

culture_qut_gt = fanstatic.Resource(
    library, 'cultures/globalize.culture.qut-GT.js', depends=[globalize])

culture_qut = fanstatic.Resource(
    library, 'cultures/globalize.culture.qut.js', depends=[globalize])

culture_quz_bo = fanstatic.Resource(
    library, 'cultures/globalize.culture.quz-BO.js', depends=[globalize])

culture_quz_ec = fanstatic.Resource(
    library, 'cultures/globalize.culture.quz-EC.js', depends=[globalize])

culture_quz_pe = fanstatic.Resource(
    library, 'cultures/globalize.culture.quz-PE.js', depends=[globalize])

culture_quz = fanstatic.Resource(
    library, 'cultures/globalize.culture.quz.js', depends=[globalize])

culture_rm_ch = fanstatic.Resource(
    library, 'cultures/globalize.culture.rm-CH.js', depends=[globalize])

culture_rm = fanstatic.Resource(
    library, 'cultures/globalize.culture.rm.js', depends=[globalize])

culture_ro_ro = fanstatic.Resource(
    library, 'cultures/globalize.culture.ro-RO.js', depends=[globalize])

culture_ro = fanstatic.Resource(
    library, 'cultures/globalize.culture.ro.js', depends=[globalize])

culture_ru_ru = fanstatic.Resource(
    library, 'cultures/globalize.culture.ru-RU.js', depends=[globalize])

culture_ru = fanstatic.Resource(
    library, 'cultures/globalize.culture.ru.js', depends=[globalize])

culture_rw_rw = fanstatic.Resource(
    library, 'cultures/globalize.culture.rw-RW.js', depends=[globalize])

culture_rw = fanstatic.Resource(
    library, 'cultures/globalize.culture.rw.js', depends=[globalize])

culture_sa_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.sa-IN.js', depends=[globalize])

culture_sa = fanstatic.Resource(
    library, 'cultures/globalize.culture.sa.js', depends=[globalize])

culture_sah_ru = fanstatic.Resource(
    library, 'cultures/globalize.culture.sah-RU.js', depends=[globalize])

culture_sah = fanstatic.Resource(
    library, 'cultures/globalize.culture.sah.js', depends=[globalize])

culture_se_fi = fanstatic.Resource(
    library, 'cultures/globalize.culture.se-FI.js', depends=[globalize])

culture_se_no = fanstatic.Resource(
    library, 'cultures/globalize.culture.se-NO.js', depends=[globalize])

culture_se_se = fanstatic.Resource(
    library, 'cultures/globalize.culture.se-SE.js', depends=[globalize])

culture_se = fanstatic.Resource(
    library, 'cultures/globalize.culture.se.js', depends=[globalize])

culture_si_lk = fanstatic.Resource(
    library, 'cultures/globalize.culture.si-LK.js', depends=[globalize])

culture_si = fanstatic.Resource(
    library, 'cultures/globalize.culture.si.js', depends=[globalize])

culture_sk_sk = fanstatic.Resource(
    library, 'cultures/globalize.culture.sk-SK.js', depends=[globalize])

culture_sk = fanstatic.Resource(
    library, 'cultures/globalize.culture.sk.js', depends=[globalize])

culture_sl_si = fanstatic.Resource(
    library, 'cultures/globalize.culture.sl-SI.js', depends=[globalize])

culture_sl = fanstatic.Resource(
    library, 'cultures/globalize.culture.sl.js', depends=[globalize])

culture_sma_no = fanstatic.Resource(
    library, 'cultures/globalize.culture.sma-NO.js', depends=[globalize])

culture_sma_se = fanstatic.Resource(
    library, 'cultures/globalize.culture.sma-SE.js', depends=[globalize])

culture_sma = fanstatic.Resource(
    library, 'cultures/globalize.culture.sma.js', depends=[globalize])

culture_smj_no = fanstatic.Resource(
    library, 'cultures/globalize.culture.smj-NO.js', depends=[globalize])

culture_smj_se = fanstatic.Resource(
    library, 'cultures/globalize.culture.smj-SE.js', depends=[globalize])

culture_smj = fanstatic.Resource(
    library, 'cultures/globalize.culture.smj.js', depends=[globalize])

culture_smn_fi = fanstatic.Resource(
    library, 'cultures/globalize.culture.smn-FI.js', depends=[globalize])

culture_smn = fanstatic.Resource(
    library, 'cultures/globalize.culture.smn.js', depends=[globalize])

culture_sms_fi = fanstatic.Resource(
    library, 'cultures/globalize.culture.sms-FI.js', depends=[globalize])

culture_sms = fanstatic.Resource(
    library, 'cultures/globalize.culture.sms.js', depends=[globalize])

culture_sq_al = fanstatic.Resource(
    library, 'cultures/globalize.culture.sq-AL.js', depends=[globalize])

culture_sq = fanstatic.Resource(
    library, 'cultures/globalize.culture.sq.js', depends=[globalize])

culture_sr_cyrl_ba = fanstatic.Resource(
    library, 'cultures/globalize.culture.sr-Cyrl-BA.js', depends=[globalize])

culture_sr_cyrl_cs = fanstatic.Resource(
    library, 'cultures/globalize.culture.sr-Cyrl-CS.js', depends=[globalize])

culture_sr_cyrl_me = fanstatic.Resource(
    library, 'cultures/globalize.culture.sr-Cyrl-ME.js', depends=[globalize])

culture_sr_cyrl_rs = fanstatic.Resource(
    library, 'cultures/globalize.culture.sr-Cyrl-RS.js', depends=[globalize])

culture_sr_cyrl = fanstatic.Resource(
    library, 'cultures/globalize.culture.sr-Cyrl.js', depends=[globalize])

culture_sr_latn_ba = fanstatic.Resource(
    library, 'cultures/globalize.culture.sr-Latn-BA.js', depends=[globalize])

culture_sr_latn_cs = fanstatic.Resource(
    library, 'cultures/globalize.culture.sr-Latn-CS.js', depends=[globalize])

culture_sr_latn_me = fanstatic.Resource(
    library, 'cultures/globalize.culture.sr-Latn-ME.js', depends=[globalize])

culture_sr_latn_rs = fanstatic.Resource(
    library, 'cultures/globalize.culture.sr-Latn-RS.js', depends=[globalize])

culture_sr_latn = fanstatic.Resource(
    library, 'cultures/globalize.culture.sr-Latn.js', depends=[globalize])

culture_sr = fanstatic.Resource(
    library, 'cultures/globalize.culture.sr.js', depends=[globalize])

culture_sv_fi = fanstatic.Resource(
    library, 'cultures/globalize.culture.sv-FI.js', depends=[globalize])

culture_sv_se = fanstatic.Resource(
    library, 'cultures/globalize.culture.sv-SE.js', depends=[globalize])

culture_sv = fanstatic.Resource(
    library, 'cultures/globalize.culture.sv.js', depends=[globalize])

culture_sw_ke = fanstatic.Resource(
    library, 'cultures/globalize.culture.sw-KE.js', depends=[globalize])

culture_sw = fanstatic.Resource(
    library, 'cultures/globalize.culture.sw.js', depends=[globalize])

culture_syr_sy = fanstatic.Resource(
    library, 'cultures/globalize.culture.syr-SY.js', depends=[globalize])

culture_syr = fanstatic.Resource(
    library, 'cultures/globalize.culture.syr.js', depends=[globalize])

culture_ta_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.ta-IN.js', depends=[globalize])

culture_ta = fanstatic.Resource(
    library, 'cultures/globalize.culture.ta.js', depends=[globalize])

culture_te_in = fanstatic.Resource(
    library, 'cultures/globalize.culture.te-IN.js', depends=[globalize])

culture_te = fanstatic.Resource(
    library, 'cultures/globalize.culture.te.js', depends=[globalize])

culture_tg_cyrl_tj = fanstatic.Resource(
    library, 'cultures/globalize.culture.tg-Cyrl-TJ.js', depends=[globalize])

culture_tg_cyrl = fanstatic.Resource(
    library, 'cultures/globalize.culture.tg-Cyrl.js', depends=[globalize])

culture_tg = fanstatic.Resource(
    library, 'cultures/globalize.culture.tg.js', depends=[globalize])

culture_th_th = fanstatic.Resource(
    library, 'cultures/globalize.culture.th-TH.js', depends=[globalize])

culture_th = fanstatic.Resource(
    library, 'cultures/globalize.culture.th.js', depends=[globalize])

culture_tk_tm = fanstatic.Resource(
    library, 'cultures/globalize.culture.tk-TM.js', depends=[globalize])

culture_tk = fanstatic.Resource(
    library, 'cultures/globalize.culture.tk.js', depends=[globalize])

culture_tn_za = fanstatic.Resource(
    library, 'cultures/globalize.culture.tn-ZA.js', depends=[globalize])

culture_tn = fanstatic.Resource(
    library, 'cultures/globalize.culture.tn.js', depends=[globalize])

culture_tr_tr = fanstatic.Resource(
    library, 'cultures/globalize.culture.tr-TR.js', depends=[globalize])

culture_tr = fanstatic.Resource(
    library, 'cultures/globalize.culture.tr.js', depends=[globalize])

culture_tt_ru = fanstatic.Resource(
    library, 'cultures/globalize.culture.tt-RU.js', depends=[globalize])

culture_tt = fanstatic.Resource(
    library, 'cultures/globalize.culture.tt.js', depends=[globalize])

culture_tzm_latn_dz = fanstatic.Resource(
    library, 'cultures/globalize.culture.tzm-Latn-DZ.js', depends=[globalize])

culture_tzm_latn = fanstatic.Resource(
    library, 'cultures/globalize.culture.tzm-Latn.js', depends=[globalize])

culture_tzm = fanstatic.Resource(
    library, 'cultures/globalize.culture.tzm.js', depends=[globalize])

culture_ug_cn = fanstatic.Resource(
    library, 'cultures/globalize.culture.ug-CN.js', depends=[globalize])

culture_ug = fanstatic.Resource(
    library, 'cultures/globalize.culture.ug.js', depends=[globalize])

culture_uk_ua = fanstatic.Resource(
    library, 'cultures/globalize.culture.uk-UA.js', depends=[globalize])

culture_uk = fanstatic.Resource(
    library, 'cultures/globalize.culture.uk.js', depends=[globalize])

culture_ur_pk = fanstatic.Resource(
    library, 'cultures/globalize.culture.ur-PK.js', depends=[globalize])

culture_ur = fanstatic.Resource(
    library, 'cultures/globalize.culture.ur.js', depends=[globalize])

culture_uz_cyrl_uz = fanstatic.Resource(
    library, 'cultures/globalize.culture.uz-Cyrl-UZ.js', depends=[globalize])

culture_uz_cyrl = fanstatic.Resource(
    library, 'cultures/globalize.culture.uz-Cyrl.js', depends=[globalize])

culture_uz_latn_uz = fanstatic.Resource(
    library, 'cultures/globalize.culture.uz-Latn-UZ.js', depends=[globalize])

culture_uz_latn = fanstatic.Resource(
    library, 'cultures/globalize.culture.uz-Latn.js', depends=[globalize])

culture_uz = fanstatic.Resource(
    library, 'cultures/globalize.culture.uz.js', depends=[globalize])

culture_vi_vn = fanstatic.Resource(
    library, 'cultures/globalize.culture.vi-VN.js', depends=[globalize])

culture_vi = fanstatic.Resource(
    library, 'cultures/globalize.culture.vi.js', depends=[globalize])

culture_wo_sn = fanstatic.Resource(
    library, 'cultures/globalize.culture.wo-SN.js', depends=[globalize])

culture_wo = fanstatic.Resource(
    library, 'cultures/globalize.culture.wo.js', depends=[globalize])

culture_xh_za = fanstatic.Resource(
    library, 'cultures/globalize.culture.xh-ZA.js', depends=[globalize])

culture_xh = fanstatic.Resource(
    library, 'cultures/globalize.culture.xh.js', depends=[globalize])

culture_yo_ng = fanstatic.Resource(
    library, 'cultures/globalize.culture.yo-NG.js', depends=[globalize])

culture_yo = fanstatic.Resource(
    library, 'cultures/globalize.culture.yo.js', depends=[globalize])

culture_zh_chs = fanstatic.Resource(
    library, 'cultures/globalize.culture.zh-CHS.js', depends=[globalize])

culture_zh_cht = fanstatic.Resource(
    library, 'cultures/globalize.culture.zh-CHT.js', depends=[globalize])

culture_zh_cn = fanstatic.Resource(
    library, 'cultures/globalize.culture.zh-CN.js', depends=[globalize])

culture_zh_hk = fanstatic.Resource(
    library, 'cultures/globalize.culture.zh-HK.js', depends=[globalize])

culture_zh_hans = fanstatic.Resource(
    library, 'cultures/globalize.culture.zh-Hans.js', depends=[globalize])

culture_zh_hant = fanstatic.Resource(
    library, 'cultures/globalize.culture.zh-Hant.js', depends=[globalize])

culture_zh_mo = fanstatic.Resource(
    library, 'cultures/globalize.culture.zh-MO.js', depends=[globalize])

culture_zh_sg = fanstatic.Resource(
    library, 'cultures/globalize.culture.zh-SG.js', depends=[globalize])

culture_zh_tw = fanstatic.Resource(
    library, 'cultures/globalize.culture.zh-TW.js', depends=[globalize])

culture_zh = fanstatic.Resource(
    library, 'cultures/globalize.culture.zh.js', depends=[globalize])

culture_zu_za = fanstatic.Resource(
    library, 'cultures/globalize.culture.zu-ZA.js', depends=[globalize])

culture_zu = fanstatic.Resource(
    library, 'cultures/globalize.culture.zu.js', depends=[globalize])

