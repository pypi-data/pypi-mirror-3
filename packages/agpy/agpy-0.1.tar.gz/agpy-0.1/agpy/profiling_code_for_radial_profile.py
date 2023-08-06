"""
        if profile:

            # Find out which radial bin each point in the map belongs to
            whichbin = np.digitize(r.flat,bins)
            # original, one line
            radial_prof_orig = np.array([(image*weights).flat[mask.flat*(whichbin==b)].sum() / weights.flat[mask.flat*(whichbin==b)].sum() for b in xrange(1,nbins+1)])
            # original
            radial_prof_e = np.zeros(nbins)
            for b in xrange(1,nbins+1):
                flat_weighted_image = (image*weights).ravel()
                rad_sum = flat_weighted_image[mask.flat*(whichbin==b)].sum()
                weight_sum = weights.flat[mask.flat*(whichbin==b)].sum()
                radial_prof_e[b-1] = rad_sum/weight_sum

            # slowest
            sortorder = np.argsort(whichbin)
            radial_prof_a = np.zeros(nbins,dtype='float')
            weights_a = np.zeros(nbins,dtype='float')
            maskim = (image*mask).ravel()
            for ind in sortorder:
                radial_prof_a[whichbin[ind]-1] += maskim[ind]
                weights_a[whichbin[ind]-1] += mask.flat[ind]
            radial_prof_b = radial_prof_a/weights_a

            # this is the only slow line, but it's twice as fast as the original
            # yt-version inverse_bin_indices = dict( [(bin,np.nonzero(whichbin==bin)[0]) for bin in xrange(1,nbins+1)] )
            inverse_bin_indices = [np.nonzero(whichbin==bin)[0] for bin in xrange(1,nbins+1)] 
            inverse_bin_indices_b = np.histogram(whichbin,bins=range(1,nbins+1))
            # the rest of this is reasonably fast...
            radial_prof_c = np.zeros(nbins,dtype='float')
            weights_c = np.zeros(nbins,dtype='float')
            for binnum in xrange(nbins):
                radial_prof_c[binnum] += maskim[inverse_bin_indices[binnum]].sum()
                weights_c[binnum] += mask.flat[inverse_bin_indices[binnum]].sum()
            radial_prof_d = radial_prof_c/weights_c

            import pylab
            print "orig == b?    ",sum(radial_prof_orig==radial_prof_b),"/",len(radial_prof)," chi^2: ",sum((radial_prof_orig-radial_prof_b)**2)
            print "orig == d?    ",sum(radial_prof_orig==radial_prof_d),"/",len(radial_prof)," chi^2: ",sum((radial_prof_orig-radial_prof_d)**2)
            print "orig == e?    ",sum(radial_prof_orig==radial_prof_e),"/",len(radial_prof)," chi^2: ",sum((radial_prof_orig-radial_prof_e)**2)
            print "orig == hist? ",sum(radial_prof_orig==radial_prof  ),"/",len(radial_prof)," chi^2: ",sum((radial_prof_orig-radial_prof  )**2)
            pylab.figure(1)
            pylab.clf()
            pylab.plot(radial_prof     -radial_prof,label='zero')
            pylab.plot(radial_prof_orig-radial_prof,label='orig')
            pylab.plot(radial_prof_b   -radial_prof,label='b')
            pylab.plot(radial_prof_d   -radial_prof,label='d')
            pylab.plot(radial_prof_e   -radial_prof,label='e')
            leg=pylab.legend(loc='best')
            leg.draggable()
            pylab.draw()

            if (sum((radial_prof-radial_prof_e)**2) > 1e-4 or
                sum((radial_prof-radial_prof_d)**2) > 1e-4 or
                sum((radial_prof-radial_prof_b)**2) > 1e-4):
                raise ValueError("One of the methods failed.")

        

    #import pdb; pdb.set_trace()
"""
