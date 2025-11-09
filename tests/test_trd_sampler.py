def test_trd_sampler_exists():
    from src.data.trd_sampler import TRDSampler
    s = TRDSampler()
    assert hasattr(s, "sample")
