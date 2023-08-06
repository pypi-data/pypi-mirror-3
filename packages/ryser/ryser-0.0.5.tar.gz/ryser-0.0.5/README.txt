=========================================
Ryser - Latin Squares and Related Designs
=========================================
Copyright Matthew Henderson, 2012
Created Wed Aug  8 15:39:10 BST 2012. Last updated Tue Aug 21 15:17:52 BST 2012

Ryser is a Python package for latin squares and related designs.

An Example
==========

Here is a demo which computes Hall numbers and draws subgraphs.

    from ryser.examples import eg3, fail4
    from ryser.hall import hall_inequality_on_cells, \
                               symmetric_hall_inequality_on_cells

    S = fail4[0]

    assert hall_inequality_on_cells(eg3, S)
    assert not symmetric_hall_inequality_on_cells(eg3, S)

    from ryser.hall import symmetric_hall_numbers, hall_subgraphs

    hall_nums = symmetric_hall_numbers(eg3, S)

    print "S: " + str(S)
    print "Hall numbers: "  + str(hall_nums)
    print "Sum of Hall numbers: " + str(sum(hall_nums))
    print "No of vertices: " + str(len(S))

    hall_subgraphs(eg3, S, format = 'dot')

