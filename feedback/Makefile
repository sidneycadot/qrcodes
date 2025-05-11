
DOCROOT=ISO_IEC_18004_SuggestedImprovements

.PHONY : clean default

$(DOCROOT).pdf $(DOCROOT).aux $(DOCROOT).log : $(DOCROOT).tex
	pdflatex $(DOCROOT)
	pdflatex $(DOCROOT)

clean :
	$(RM) $(DOCROOT).pdf $(DOCROOT).aux $(DOCROOT).log
