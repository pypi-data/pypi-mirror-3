<div class='content'>
<h1>Mis programas</h1>

<button onClick='crear_un_nuevo_programa()'>Crear un programa nuevo</button>

<p>

<ul>
%for x in  programas:
  <li><a onclick='cargar_programa(this)' href='#{{x}}'>{{x}}</a></li>
%end
</ul>
</div>

%rebase layout title='mis programas'

