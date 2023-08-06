
    def test_free_types(self):
        import weakref, gc
        ffi = FFI(backend=self.Backend())
        BTypes = [ffi.typeof("int" + "*" * i) for i in range(20)]
        refs = [weakref.ref(BType) for BType in BTypes]
        #
        BType = None
        BTypes = None
        for i in range(5):
            alives = None
            gc.collect()
            alives = [ref() for ref in refs]
            alives = filter(None, alives)
            if len(alives) <= 3:
                break
        else:
            raise AssertionError("types are not freed: %r" % alives)
