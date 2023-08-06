
CXX = g++ -fPIC
CXXFLAGS = -O3
AR = ar

all: fileformat.pb.h osmformat.pb.h libosmpbf_pic.a

libosmpbf_pic.a: fileformat.pb.o osmformat.pb.o
	$(AR) -cr $@ fileformat.pb.o osmformat.pb.o

%.pb.o: %.pb.cc
	$(CXX) $(CXXFLAGS) -c -o $@ $<

%.pb.cc %.pb.h: %.proto
	protoc --proto_path=. --cpp_out=. $<

clean:
	rm -f *.pb.h *.pb.cc *.pb.o libosmpbf.a

