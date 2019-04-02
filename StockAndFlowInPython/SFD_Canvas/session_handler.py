import xml.dom.minidom
from StockAndFlowInPython.Graph_SD.graph_based_engine import Session, function_names
from StockAndFlowInPython.parsing.XMILE_parsing import parsing_equation


def name_handler(name):
    return name.replace(' ', '_').replace('\n', '_')


class SessionHandler(object):
    def __init__(self):
        self.sess1 = Session()

    def add_angle_to_eqn(self, name, eqn):
        if eqn[0] in function_names:
            for factor in eqn[1:]:
                if type(factor[0]) == str:
                    factor[1] = self.get_angle(to_element=name, from_element=factor[0])
            return eqn
        else:
            return eqn

    def get_angle(self, from_element, to_element):
        for connection_view_array in self.connection_views_array:
            if connection_view_array[3] == to_element:
                if connection_view_array[2] == from_element:
                    return connection_view_array[1]

    def read_xmile_model(self, filename):
        DOMTree = xml.dom.minidom.parse(filename)
        self.model = DOMTree.documentElement

        # fetch all variables in the file
        # since there is only one "variables" in the file, the outcome
        # is a list containing only one element of "variables"

        allvariables = self.model.getElementsByTagName("variables")

        # fetch all stocks/flows/aux/connectors in all variables (the only element in the list)

        self.stock_definitions = allvariables[0].getElementsByTagName("stock")
        self.flow_definitions = allvariables[0].getElementsByTagName("flow")
        self.aux_definitions = allvariables[0].getElementsByTagName("aux")

        # fetch all views in the file ---> down to the view

        self.all_views = self.model.getElementsByTagName("views")
        self.views = self.all_views[0].getElementsByTagName("view")

        # fetch views for all connectors and draw
        self.connectorviews = []
        for connectorview in self.views[0].getElementsByTagName("connector"):
            if connectorview.hasAttribute("uid"):
                self.connectorviews.append(connectorview)

        self.connection_views_array = list()
        for connectorview in self.connectorviews:
            uid = connectorview.getAttribute("uid")
            angle = float(connectorview.getAttribute("angle"))
            try:
                from_element = connectorview.getElementsByTagName("from")[0].getElementsByTagName("alias")[
                    0].getAttribute('uid')
            except:
                from_element = connectorview.getElementsByTagName("from")[0].childNodes[0].data
                from_element = name_handler(from_element)

            try:
                to_element = connectorview.getElementsByTagName("to")[0].getElementsByTagName("alias")[0].getAttribute(
                    'uid')
            except:
                to_element = connectorview.getElementsByTagName("to")[0].childNodes[0].data
                to_element = name_handler(to_element)

            # print("From and to", from_element, to_element)
            print('formatting connector', uid, angle, 'from:', from_element, 'to:', to_element)
            # self.sess1.add_connector(uid=uid, angle=angle, from_element=from_element, to_element=to_element)
            self.connection_views_array.append([uid, angle, from_element, to_element])

        # fetch views for all stocks and draw
        self.stockviews = []
        for stockview in self.views[0].getElementsByTagName("stock"):
            if stockview.hasAttribute("name"):
                self.stockviews.append(stockview)

        for stockview in self.stockviews:
            name = stockview.getAttribute("name")
            name = name_handler(name)
            # print("Adding this stock:", name)
            for stock_definition in self.stock_definitions:  # Loop to find a particular stock
                if name_handler(stock_definition.getAttribute("name")) == name:
                    eqn = stock_definition.getElementsByTagName("eqn")[0].firstChild.data
            x = float(stockview.getAttribute("x"))
            y = float(stockview.getAttribute("y"))
            print('adding stock', name)
            self.sess1.add_stock(name=name, equation=self.add_angle_to_eqn(name=name, eqn=parsing_equation(eqn)), x=x, y=y)

        # fetch views for all flows and draw
        self.flowviews = []
        for flowview in self.views[0].getElementsByTagName("flow"):
            if flowview.hasAttribute("name"):
                self.flowviews.append(flowview)

        for flowview in self.flowviews:
            name = flowview.getAttribute("name")
            name = name_handler(name)
            # print("Adding this flow:", name)
            for flow_definition in self.flow_definitions:  # loop to find a particular flow
                if name_handler(flow_definition.getAttribute("name")) == name:
                    eqn = flow_definition.getElementsByTagName("eqn")[0].firstChild.data
            points = list()
            for point in flowview.getElementsByTagName("pt"):
                points.append((point.getAttribute("x"), point.getAttribute("y")))
            x = float(flowview.getAttribute("x"))
            y = float(flowview.getAttribute("y"))
            print('adding flow', name)
            self.sess1.add_flow(name=name, equation=self.add_angle_to_eqn(name=name, eqn=parsing_equation(eqn)), x=x, y=y, points=points)

        # fetch views for all auxiliaries and draw
        self.auxviews = []
        for auxview in self.views[0].getElementsByTagName("aux"):
            if auxview.hasAttribute("name"):
                #print(auxview.getAttribute("name"), "heeeeeeeee")
                self.auxviews.append(auxview)

        for auxview in self.auxviews:
            name = auxview.getAttribute("name")
            name = name_handler(name)
            # print("Adding this aux:", name)
            for aux_definition in self.aux_definitions:  # Loop to find a particular aux
                if name_handler(aux_definition.getAttribute("name")) == name:
                    eqn = aux_definition.getElementsByTagName("eqn")[0].firstChild.data
            x = float(auxview.getAttribute("x"))
            y = float(auxview.getAttribute("y"))
            print('adding aux', name)
            self.sess1.add_aux(name=name, equation=self.add_angle_to_eqn(name=name, eqn=parsing_equation(eqn)), x=x, y=y)

        # fetch views for all aliases and draw
        self.aliasviews = []
        for aliasview in self.views[0].getElementsByTagName("alias"):
            # distinguish definition of alias from refering to it (cannot use 'color': sometimes there isn't)
            if aliasview.hasAttribute("x"):
                #print(aliasview.getAttribute("x"), "herererere!!")
                self.aliasviews.append(aliasview)

        for aliasview in self.aliasviews:
            uid = aliasview.getAttribute("uid")
            x = float(aliasview.getAttribute("x"))
            y = float(aliasview.getAttribute("y"))
            of = aliasview.getElementsByTagName("of")[0].firstChild.data
            # print('\n', uid, 'of', of, 'bbbbbbbb\n')
            of = name_handler(of)
            print('adding alias', name)
            self.sess1.add_alias(uid=uid, of_element=of, x=x, y=y)

        print('\nnodes: ', self.sess1.structures['default'].sfd.nodes)
        print('edges: ', self.sess1.structures['default'].sfd.edges)