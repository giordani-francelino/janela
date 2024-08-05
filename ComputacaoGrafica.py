import xml.etree.ElementTree as ET
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QAction
from PyQt5.QtGui import QPainter, QPolygon
from PyQt5.QtCore import QPoint, QLine


class ProcessarArquivosXml():

    def exportar_arquivo_xml(saida, atributosTransformados):
        import xml.etree.ElementTree as ET

        # Criação do elemento raiz
        root = ET.Element("dados")

        # Adicionando elementos filhos com atributos
        for atributo in atributosTransformados:
            elemento = ET.SubElement(root, atributo["elemento"])
            for ponto in atributo["pontos"]:
                elementoPonto = ET.SubElement(elemento, ponto["nome"], attrib={"x" : str(ponto["ponto"].x()),"y" : str(ponto["ponto"].y())})
        # Criação do objeto ElementTree
        tree = ET.ElementTree(root)

        # Salvando o arquivo XML
        # tree.write(saida, encoding="utf-8", xml_declaration=True)
        with open(saida, "wb") as arquivo:
            tree.write(arquivo, encoding="utf-8", xml_declaration=True, method="xml", short_empty_elements=True)


    def  importar_arquivo_xml(entrada):
        tipo = str

        atributos = []
        try:
            # Parseia o arquivo XML
            tree = ET.parse(entrada)
            # Obtém a raiz do XML
            root = tree.getroot()
            
            # Aqui você pode processar os dados do XML conforme necessário
            # Por exemplo, imprimir o nome e o valor de cada elemento
            for atributo in root:
                pontos = []
                # print(atributo.tag, atributo.attrib, atributo.text)
                for elemento in atributo:
                    x = float(elemento.attrib["x"])
                    y = float(elemento.attrib["y"])
                    ponto = {"nome": elemento.tag, "ponto": QPoint(int(x),int(y))}
                    pontos.append(ponto)
                    # print(elemento.tag, elemento.attrib["x"], elemento.text)
                objeto = {"elemento": atributo.tag,'pontos': pontos}
                atributos.append(objeto)

                
        except FileNotFoundError:
            print(f"O arquivo '{entrada}' não foi encontrado.")
        except ET.ParseError as e:
            print(f"Erro ao analisar o arquivo XML: {e}")

        return atributos

class TransformadaViewPort():
    def transformar(atributos):
        atributosTransformados = []
        vpMin = QPoint
        vpMax = QPoint
        wMin = QPoint
        wMax = QPoint
        vpX = int
        vpY = int
        for atributo in atributos:
            pontos = []
            if (atributo["elemento"]=="viewport"):
                for ponto in atributo["pontos"]:
                    pontos.append(ponto["ponto"])
                vpMin = pontos[0]
                vpMax = pontos[1]
            if (atributo["elemento"]=="window"):
                for ponto in atributo["pontos"]:
                    pontos.append(ponto["ponto"])
                wMin = pontos[0]
                wMax = pontos[1]

        for atributo in atributos:
            pontos = []
            for elemento in atributo["pontos"]:
                vpX = ((elemento["ponto"].x() - wMin.x())/(wMax.x()-wMin.x()))*(vpMax.x()-vpMin.x())
                vpY = (1.0-(elemento["ponto"].y() - wMin.y())/(wMax.y()-wMin.y()))*(vpMax.y()-vpMin.y())
                if atributo["elemento"]=='viewport':
                    vpX = elemento["ponto"].x()
                    vpY = elemento["ponto"].y()
                ponto = {"nome": elemento["nome"], "ponto": QPoint(int(vpX),int(vpY))}
                pontos.append(ponto)
            objeto = {"elemento": atributo["elemento"],'pontos': pontos}
            atributosTransformados.append(objeto)

        return atributosTransformados
            

class DesenhaObjetos(QWidget):
    def __init__(self, atributosTransformados):
        super().__init__()
        self.atributosTransformados = atributosTransformados

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

    

        # Cria um polígono com as coordenadas especificadas
        # polygon = QPolygon(self.points)

        # Desenha o polígono na janela
        for atributo in self.atributosTransformados:
            pontos = []
            if (atributo["elemento"]=="poligono"):
                for ponto in atributo["pontos"]:
                    pontos.append(ponto["ponto"])
                # print(pontos)
                painter.drawPolygon(pontos)
            elif (atributo["elemento"]=="reta"):
                for ponto in atributo["pontos"]:
                    pontos.append(ponto["ponto"])
                # print(pontos)
                painter.drawLine(pontos[0],pontos[1])
            elif (atributo["elemento"]=="pontos"):
                for ponto in atributo["pontos"]:
                    painter.drawPoint(ponto["ponto"])

    def limparTela(self):
        self.atributosTransformados.clear()
        self.update()

class MainVeiWPort(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Chama a função para importar o arquivo XML
        atributos = ProcessarArquivosXml.importar_arquivo_xml("entrada.xml")    

        # atribuir o tamanho da janela
        self.setWindowTitle("Desenhar polígonos, retas e pontos")
        for atributo in atributos:
            pontos = []
            if (atributo["elemento"]=="viewport"):
                for ponto in atributo["pontos"]:
                    pontos.append(ponto["ponto"])
                self.setGeometry(pontos[0].x(), pontos[0].y(), pontos[1].x(), pontos[1].y())

        # Chama a função para transformada de veiwport
        atributosTransformados = TransformadaViewPort.transformar(atributos)

        # gera o arquivo de saida
        ProcessarArquivosXml.exportar_arquivo_xml("saida.xml", atributosTransformados)    

        # desenha os objetos na tela
        self.central_widget = DesenhaObjetos(atributosTransformados)
        self.setCentralWidget(self.central_widget)
        self.move(50,50)
        self.initUI()


    def initUI(self):
        #    self.setWindowTitle('QMainWindow com QPainter')
        #    self.setGeometry(100, 100, 800, 600)

            # Criar uma barra de menu
            # menubar = self.menuBar()
            # menuArquivo = menubar.addMenu('Arquivo')

            # Adicionar ações ao menu
            adicionarPonto = QAction('Adicionar Ponto', self)
            #adicionarPonto.triggered.connect(self.add_rectangle)
            # menuArquivo.addAction(adicionarPonto)

            adicionarReta = QAction('Adicionar Reta', self)
            adicionarPoligono = QAction('Adicionar Polígono', self)

            limpar = QAction('Limpar', self)
            limpar.triggered.connect(self.limparTela)
            # menuArquivo.addAction(limpar)

            restaurar = QAction('Restaurar', self)
            restaurar.triggered.connect(self.restauraTelaInicial)


            # Criar uma barra de ferramentas
            toolbar = self.addToolBar('Toolbar')
            toolbar.addAction(adicionarPonto)
            toolbar.addAction(adicionarReta)
            toolbar.addAction(adicionarPoligono)
            toolbar.addAction(limpar)
            toolbar.addAction(restaurar)
    def limparTela(self):
        self.central_widget.limparTela()
    def restauraTelaInicial(self):
        self.__init__
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    veiWPort = MainVeiWPort()
    veiWPort.show()
    sys.exit(app.exec_())