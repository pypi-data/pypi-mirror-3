
all: 
	/opt/local/bin/python ./setup.py build


clean:
	$(RM) -r build
	$(RM) $(WRAPPERS)
	$(RM) $(PROXIES)
debug:
	g++ -pg -g -fno-omit-frame-pointer -O2 -Wall -c -fmessage-length=0 -MMD -MP -MF"c_lmm.d" -MT"c_lmm.d" -o "c_lmm.o" "c_lmm.cpp"
	g++ -pg -g -fno-omit-frame-pointer -O2 -Wall -c -fmessage-length=0 -MMD -MP -MF"main_testing.d" -MT"main_testing.d" -o "main_testing.o" "main_testing.cpp"
	g++ -pg -o "Clmm"  ./c_lmm.o ./main_testing.o 