"""Source-preserving compact transcription of DGCA-derived 2022–2025 annual rows.

Values are stored base36 for compactness in this distributable project.
Source CSV: https://github.com/mkubicek/india-aviation-stats
Code format: <IATA 3 letters><d domestic|i international><base36 passengers>.
"""
from pathlib import Path
import csv

COMPACT={
2022:'''AGRd2ga5.AGXdvcl.AJLd6j29.AMDd4fjtv.ATQdyoa2.BBId1y51q.BDQdlevc.BEKd35js.BHJds23.BHOdm07c.BHUd16zw.BKBdl56.BLRdeict3.BOMdhphfw.CCJdb14q.CCUd8udna.CDPd10rd.CJBd1apar.COKd2fesl.DBRddi6p.DEDdwndx.DELdrh1cw.DEPdyrf.DGHd9ud1.DHMd3s3g.DIBde0ws.DIUdtg0.DMUd5sqe.GAUd2vm6u.GAYd2ki5.GBId1sue.GDBdepd.GOId4hiy3.GOPdeoev.GWLd4sfm.HBXd5tdg.HDOdkiw.HGId5o2.HJRddv8.HYDd9iqj2.IDRd1hza1.IMFdn5y4.ISKd26h3.IXAdre5w.IXBd1id87.IXCd1ys78.IXDdbq7k.IXEdp78k.IXGd72oe.IXIdncv.IXJdxlkm.IXKd390.IXLdnzwn.IXMdhtxn.IXPd5yn.IXRd1bop1.IXSd880c.IXTd94t.IXUd8in9.IXXd5p5.IXYd232z.IXZdoj75.JAId2bqnc.JDHdi4ck.JGAd2dif.JGBd1b40.JLGd1fi.JLRd98h3.JRGd52iv.JRHd2vvo.JSAd1pgn.KBKdkez.KJBdskv.KLHd2n87.KNUd5grn.KQHd1xnr.KUUddyx.LKOd2emub.MAAd7bc1o.MAQd83l9.MYQd3ka3.NAGd1bfge.NDCd3u6.PABdocd.PATd26c8y.PBDdfzq.PGHd1i96.PNQd47rc3.PNYd1cfa.PYBdvh.PYGdsia.RAJdf40g.RJAd83c0.RPRd18zb5.RUPd11of.SAGde3kz.SDWdsxv.SHLd2706.SLVd3wn.STVdoptt.SXRd2ihf0.TCRd418p.TEIdfuv.TEZd3jt.TIRdj66p.TRVdvd7m.TRZd73l3.UDRdpayg.VDYd79t.VGAdh6c8.VNSd1bp64.VTZd1bk33.ZERd4p.AMDipumx.ATQidn8c.BLRi1pdqx.BOMi5405p.CCJi1cjko.CCUiwwqn.CJBi3kqb.COKi27tkr.DELi7tvtu.GAUi7e.GAYiegm.HYDi1si0d.IDRias0.IXBi13v.IXCi2gge.IXEiaq9l.IXMi3pjo.JAIi7npu.LKOiieel.MAAi2ecsz.MAQigpnp.NAGi1368.PNQi2eat.STVimm8.SXRiq1.TRViy0ap.TRZikt49.VGAiloe.VNSi256o.VTZi13oc''',
2023:'''AGRd3ahr.AGXdtsi.AIPd7j.AJLd84lu.AMDd5wdhv.ATQd17cpb.AYJdbs.BBId2nsxy.BDQdptwe.BEKd2pi0.BHJd18to.BHOdrzkf.BHUd1o8x.BKBd4v0.BLRdjdiir.BOMdmjg14.BUPd29x.CCJdd58m.CCUda6mx6.CDPd1kju.CJBd1lgg7.COHd1lr.COKd3asq9.DBRdch7g.DEDdyikz.DELdvzliu.DEPd3ds0.DGHdbofa.DHMd4ej5.DIBdffj2.DIUdxr1.DMUd6m86.GAUd3k58q.GAYd4g5i.GBId18zj.GDBd18j.GOId45x08.GOPdfmgv.GOXd28he5.GWLd5wlo.HBXd7r41.HDOd1p2.HGId2wy2.HJRd1880.HSRd6yxp.HYDdc176z.IDRd21ri9.IMFdqb86.ISKd4tpb.IXAdub49.IXBd1uv3m.IXCd24t6g.IXDddowm.IXEdtvoo.IXGd62ri.IXIdovt.IXJdwdks.IXKda2k.IXLdmbn6.IXMdmhte.IXRd1jlep.IXSd8pvw.IXTd6nq.IXUdcv36.IXWd5cx.IXXdfsd.IXYd1pjh.IXZdtixu.JAId2xb0w.JDHdnogc.JGAd37zr.JGBd1e7j.JLRd7qgp.JRGd4uli.JRHd3ifp.JSAd2idv.KBKdh5y.KJBdtpw.KLHd3ddc.KNUd5z5l.KQHdjjh.KUUdcfm.LKOd39s2l.LUHdi8.MAAd91akq.MAQd8odb.MYQd2vps.NAGd1o2sz.PABdoe0.PATd261uy.PGHd28ms.PNQd5ofeh.PNYd143l.PYBd7ou.PYGd7w3.RAJdcs29.RJAd8qtq.RPRd1gi6k.RQYdeyw.RRKdl1f.RUPdyk1.SAGdfkac.SDWdd0q.SHLd35g5.SLVddrr.STVdrlju.SXRd2g0b6.SXVdc8o.TCRd46ss.TEIdocx.TEZdln0.TIRdj6p5.TRVd1avx8.TRZd9a8m.UDRdwmre.UKEdfb.VDYdwix.VGAdkd41.VNSd1nx98.VTZd1p4ry.ZERd8e.AMDix0nc.ATQijqoc.BBIi1gkt.BLRi2i19f.BOMi7ne17.CCJi1j5z4.CCUi1dnp2.CJBi4ef6.COKi2rv6m.DELiaku6b.GAUi7bi.GAYi1cll.GOXi95t9.HYDi2ig2t.IDRir50.IXBi5qd.IXCi37g2.IXEib1xl.IXMi4oft.JAIi86pd.LKOiif8v.MAAi38ute.MAQihcwv.NAGi1ybf.PNQi3qm8.STVi17dj.TRVi13fv6.TRZiqve9.VGAiqk7.VNSi2f0g.VTZi1flx''',
2024:'''AGRd3mjd.AGXd1uk0.AHAd31.AIPdk1i.AJLda0ey.AMDd6b8tx.ATQd1ctvv.AYJdldt9.AZHdt1.BBId2n74o.BDQdq5ob.BEKd2ji7.BHJd36r2.BHOdwlev.BHUd1m1z.BKBd6nj.BLRdkqrdc.BOMdn5oge.BUPdlw5.CCJdes8p.CCUdb1q3n.CDPdz1c.CJBd1pe31.COHd3x4.COKd3deh6.CWKdz7.DBRdacse.DEDdz3j9.DELdx8w25.DEPd4w4u.DGHda9i1.DHMd4ede.DIBdhbjx.DIUd248a.DMUd6qxj.GAUd3nebj.GAYd4sro.GBIdvi5.GDBdn8b.GOId3xpw5.GOPdfvv5.GOXd2nj7g.GWLd8cg1.HBXd76cr.HDOd1lir.HGId3l2v.HJRd13ue.HRHd134.HSRdm7le.HYDddsqod.IDRd27dqb.IMFdra4u.ISKd6inz.IXAdtbmw.IXBd1xll1.IXCd26rp6.IXDdcawg.IXEdzh5n.IXGd71x0.IXIdr9e.IXJdwp13.IXKdcr3.IXLdmb3h.IXMdm7sf.IXRd1iont.IXSd9in9.IXTd6e6.IXUdeqf2.IXWd6qo.IXYd1cq6.IXZdy5x0.JAId35dw9.JDHdlz07.JGAd3c2k.JGBd1i1g.JLGd1drp.JLRd7mb3.JRGd6667.JRHd2xye.JSAd2rxg.KJBdgu2.KLHd3bcb.KNUd611n.KQHd1q4w.KUUdlfp.LKOd3bjhz.LUHd1cg.MAAd9ive6.MAQd83is.MYQd1vof.MZSdea.NAGd1lc2d.NDCd29km.NNSd5wr.PABdsc5.PATd25flc.PGHd24v1.PNQd62dkl.PNYdkcz.PYBd8nd.PYGd9wd.REWd8p.RJAd9cfd.RPRd1hsmo.RQYd22kg.RRKdvgm.RUPd3yi.SAGdg8c7.SDWdfkp.SHLd3dc2.SLVdi7c.STVdx88d.SXRd2hwd4.SXVd2m7b.TCRd4o94.TEId4os.TEZd113v.TIRdjxqq.TRVd1jpbb.TRZdcfjy.UDRdxw8k.UKEd1sd.VDYd144l.VGAdp3ty.VNSd22nzq.VSVdkm.VTZd1lz45.ZERd7m.AMDi15pe4.ATQimz7b.BBIi2nob.BLRi30u7h.BOMi8ngfw.CCJi1nqh2.CCUi1dhs6.CJBi4uoh.COKi2ze6p.DELic8vcd.GAUi13zz.GAYi1lds.GOXia91p.HYDi2tuow.IDRi10y8.IXBi672.IXCi3m7z.IXEic5ws.IXMi4w56.JAIi9314.LKOinzrt.MAAi3cmvp.MAQijlu8.NAGi24qp.PNQi4cee.STVi32b7.TRVi18d8i.TRZisdij.VGAilhn.VNSi2iti.VTZi2bxw''',
2025:'''AGRd4y3z.AGXd2id6.AHAd11o.AIPd1pea.AJLd8xci.AMDd6ru4c.ATQd16uu6.AVRd5d4.AYJdmjvw.BBId2ylw9.BDQdqnqa.BEKd2kth.BHJd5ejn.BHOdxsnh.BHUdp62.BKBdvly.BLRdlhmyl.BOMdmup1o.BUPddh4.CCJdi5ey.CCUdb4t32.CDPd1gro.CJBd1v6xk.COHd4c7.COKd3hn4l.DBRdfeze.DEDd12kpn.DELdwon85.DEPd7yk8.DGHdbhdb.DHMd3fu2.DIBdh250.DIUd2hpf.DMUd7zum.DPPdmx.GAUd3z986.GAYd568x.GBIdel8.GDBdpci.GOId3pq0u.GOPdop2t.GOXd2sa20.GWLd69pz.HBXd7snm.HDOdldfq.HGId3xc9.HJRd13im.HSRdm9we.HSSd4y0.HYDdf3hb0.IDRd2hxrw.IMFdqwfi.ISKd8liu.IXAdwhat.IXBd21qdw.IXCd27wem.IXDdmgoh.IXEd12uia.IXGd6e7y.IXId9de.IXJdtqdl.IXKd5po.IXLdjgce.IXMdoy7e.IXRd1lsrs.IXSd92cn.IXTd3ab.IXUddj6c.IXWd6qg.IXXdh9p.IXYdqxp.IXZd11ps0.JAId2zo68.JDHdlwbc.JGAd2m1x.JGBd19el.JLGd2pnq.JLRdaiaw.JRGd971t.JRHd3296.JSAd3hef.KJBdf71.KLHd3j6q.KNUd7mg4.KQHd2mif.KUUde2h.LKOd30wvr.LUHdhj.MAAda1abs.MAQd9rkk.MYQd1u8w.NAGd1o4nw.NDCd3ia6.NNSd7xb.PABduoy.PATd2jwgi.PBDd55q.PGHd1khf.PNQd6dv1g.PNYd22bn.PXNd1n7v.PYBdbfk.RAJd2gbp.REWd4cc.RJAdc829.RPRd1nhot.RQYd3omh.RRKdc46.RUPd5c2.SAGde2cl.SDWd11od.SHLd1zlz.SLVdao1.SSEdcgu.STVdyjpp.SXRd1z2qr.SXVd2jmc.TCRd5zsi.TEId8tl.TIRdquva.TRVd1d4s3.TRZdgt0e.UDRdzblb.UKEd3ft.VDYdame.VGAdt2uj.VNSd2iwh9.VTZd1qkop.ZERdki.AMDi1b9h3.ATQimvar.BBIi2xm0.BLRi3xozw.BOMi9bdvh.CCJi1rni4.CCUi1bd8t.CJBi6unj.COKi34pir.DELick2w1.GAUi10q7.GAYiyro.GOXiaigc.HYDi35dnf.IDRi1b84.IXBi5ng.IXCi3ldz.IXEif0i7.IXMi4e0i.JAIibwk0.LKOiop5a.MAAi3m82j.MAQimb6j.NAGi216z.PNQi7fqz.STVi4csm.TRVi1dmx7.TRZito8k.VGAiovq.VNSi30ra.VTZi28rg'''
}

# Complete national totals for 2016–2025 from the same airport_yearly.csv.
# Note: 2015 has international only and is omitted from full-year comparisons.
NATIONAL = [
(2016,198946866,53673140,78,24),(2017,233547462,58941573,90,25),
(2018,277396568,63210841,100,27),(2019,287472512,63661178,102,31),
(2020,125704022,17092876,105,31),(2021,165490158,16973678,109,28),
(2022,246484028,46920910,113,30),(2023,304080934,63881888,121,31),
(2024,322650506,72210403,128,31),(2025,333873006,77979936,129,31)
]

def unpack(output_dir: Path):
    output_dir.mkdir(parents=True,exist_ok=True)
    path=output_dir/'airport_yearly_2022_2025.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['year','airport','category','passengers'])
        for year,sequence in COMPACT.items():
            for item in sequence.split('.'):
                assert len(item)>=5 and item[:3].isupper() and item[3] in 'di',(year,item)
                w.writerow([year,item[:3],'domestic' if item[3]=='d' else 'international',int(item[4:],36)])
    p=output_dir/'national_2016_2025.csv'
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['year','domestic','international','domestic_reporting_airports','international_reporting_airports']);w.writerows(NATIONAL)
    return path,p

if __name__=='__main__':
    files=unpack(Path(__file__).resolve().parents[1]/'data'/'raw')
    print('Wrote',*files)
