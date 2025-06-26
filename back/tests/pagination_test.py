from django.test import Client

def test_pagination_page_size(system_client: Client, payer_generator):
    payer_generator(10)
    page_size = 5
    page = 1
    response = system_client.get(f'/api/payer/?page={page}&page_size={page_size}')

    assert response.status_code == 200, response.content
    data = response.json()['data']

    assert 'paginator' in data, "Resposta não contém 'paginator'."
    assert 'page' in data, "Resposta não contém 'page'."
    assert data['paginator']['page_size'] == page_size, f"Esperado tamanho de página {page_size}, mas retornou {data['paginator']['page_size']}."
    assert data['page']['page'] == page, f"Esperado página {page}, mas retornou {data['page']['page']}."
    assert data['paginator']['total_pages'] == data['paginator']['total_items'] // page_size + (1 if data['paginator']['total_items'] % page_size > 0 else 0), \
        f"Esperado {data['paginator']['total_pages']} páginas, mas retornou {data['paginator']['total_pages']}."
    assert 'items' in data['page'], "Resposta não contém 'items'."
    assert len(data['page']['items']) == page_size, f"Esperado {page_size} itens, mas retornou {len(data['results'])}."
